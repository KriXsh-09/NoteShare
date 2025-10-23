from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import uuid
import logging

logger = logging.getLogger(__name__)

# Constants
DEFAULT_SIGNED_URL_EXPIRY = 60  # seconds
MAX_TITLE_LENGTH = 200
MAX_FILE_NAME_LENGTH = 255
MAX_FILE_PATH_LENGTH = 500


class Note(models.Model):
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    description = models.TextField(blank=True)
    file_name = models.CharField(max_length=MAX_FILE_NAME_LENGTH, blank=True, null=True)
    file_path = models.CharField(max_length=MAX_FILE_PATH_LENGTH, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'

    def __str__(self):
        return f"{self.title} - {self.uploaded_by.username}"

    def clean(self):
        """Validate model fields"""
        super().clean()
        if self.title and len(self.title.strip()) == 0:
            raise ValidationError({'title': 'Title cannot be empty or only whitespace.'})

    def save(self, *args, **kwargs):
        """Override save to ensure clean validation"""
        self.full_clean()
        super().save(*args, **kwargs)

    # ---------------- SUPABASE UPLOAD ----------------
    def upload_to_supabase(self, file):
        """
        Uploads file to Supabase storage and saves file path.
        Backward-compatible with both old and new Supabase SDKs.
        """
        try:
            from decouple import config
            from supabase import create_client
            import requests

            # Initialize Supabase client
            SUPABASE_URL = config("SUPABASE_URL")
            SUPABASE_KEY = config("SUPABASE_KEY")
            SUPABASE_BUCKET = config("SUPABASE_BUCKET", default="notes")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

            unique_name = f"{uuid.uuid4()}_{file.name}"
            data = file.read()

            # Upload file
            res = supabase.storage.from_(SUPABASE_BUCKET).upload(unique_name, data)

            success = False
            debug_info = {"type": type(res).__name__}

            # --- Case A: Old SDK returns dict ---
            if isinstance(res, dict):
                debug_info["dict"] = res
                if res.get("Key") or res.get("path") or res.get("key"):
                    success = True

            # --- Case B: New SDK returns Response object ---
            elif hasattr(res, "status_code"):
                debug_info["status_code"] = getattr(res, "status_code", None)
                if res.status_code in (200, 201, 204):
                    try:
                        body = res.json()
                        debug_info["json"] = body
                        if isinstance(body, dict) and (body.get("Key") or body.get("path")):
                            success = True
                        else:
                            success = True  # Accept as OK
                    except Exception:
                        success = True
                else:
                    try:
                        debug_info["text"] = res.text
                    except Exception:
                        debug_info["text"] = "<unreadable response>"

            # --- Case C: Other response types ---
            else:
                debug_info["repr"] = repr(res)
                try:
                    if res:
                        success = True
                except Exception:
                    success = False

            # --- Save or raise error ---
            if success:
                self.file_name = file.name
                self.file_path = unique_name
                self.save()
                logger.info(f"✅ Successfully uploaded file {file.name} to Supabase")
                logger.debug(f"Supabase upload debug info: {debug_info}")
            else:
                logger.error(f"❌ Supabase upload failed for file {file.name}. Debug: {debug_info}")
                raise Exception(f"Upload failed: {debug_info}")

        except Exception as e:
            logger.error(f"Failed to upload file {file.name} to Supabase: {e}")
            raise Exception(f"Upload failed: {str(e)}")

    # ---------------- SUPABASE URL HELPERS ----------------
    def get_public_url(self):
        """Returns a public URL for the file."""
        if not self.file_path:
            return None

        try:
            from decouple import config
            from supabase import create_client

            SUPABASE_URL = config("SUPABASE_URL")
            SUPABASE_KEY = config("SUPABASE_KEY")
            SUPABASE_BUCKET = config("SUPABASE_BUCKET", default="notes")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

            return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(self.file_path)
        except Exception as e:
            logger.error(f"Failed to get public URL for file {self.file_path}: {e}")
            return None

    def get_signed_url(self, expires_in=DEFAULT_SIGNED_URL_EXPIRY):
        """Returns a signed temporary URL for the file."""
        if not self.file_path:
            return None

        try:
            from decouple import config
            from supabase import create_client

            SUPABASE_URL = config("SUPABASE_URL")
            SUPABASE_KEY = config("SUPABASE_KEY")
            SUPABASE_BUCKET = config("SUPABASE_BUCKET", default="notes")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

            res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(self.file_path, expires_in)

            if isinstance(res, dict):
                return res.get("signedURL") or res.get("signed_url")
            elif hasattr(res, "json"):
                try:
                    body = res.json()
                    return body.get("signedURL") or body.get("signed_url")
                except Exception:
                    return None
            return None

        except Exception as e:
            logger.error(f"Failed to get signed URL for file {self.file_path}: {e}")
            return None

    # ---------------- SUPABASE DELETE ----------------
    def delete_from_supabase(self):
        """Deletes file from Supabase storage."""
        if not self.file_path:
            return

        try:
            from decouple import config
            from supabase import create_client

            SUPABASE_URL = config("SUPABASE_URL")
            SUPABASE_KEY = config("SUPABASE_KEY")
            SUPABASE_BUCKET = config("SUPABASE_BUCKET", default="notes")
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

            supabase.storage.from_(SUPABASE_BUCKET).remove([self.file_path])
            logger.info(f"🗑️ Successfully deleted file {self.file_path} from Supabase")
        except Exception as e:
            logger.error(f"Failed to delete file {self.file_path} from Supabase: {e}")
            raise Exception(f"Delete failed: {str(e)}")

    # ---------------- UTILITIES ----------------
    @property
    def is_pdf(self):
        """Check if the file is a PDF."""
        return self.file_name and self.file_name.lower().endswith('.pdf')

    @property
    def file_size_display(self):
        """Return file size in human readable format (if available)."""
        # This would require additional metadata storage
        return "Unknown"
