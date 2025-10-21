from django.db import models
from django.contrib.auth.models import User
from decouple import config
from supabase import create_client
import uuid

# Initialize Supabase client once
SUPABASE_URL = config("SUPABASE_URL")
SUPABASE_KEY = config("SUPABASE_KEY")
SUPABASE_BUCKET = config("SUPABASE_BUCKET", default="notes")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class Note(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.uploaded_by.username}"

    def upload_to_supabase(self, file):
        """
        Uploads file to Supabase storage and saves file path.
        """
        unique_name = f"{uuid.uuid4()}_{file.name}"
        data = file.read()
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(unique_name, data)
        
        # Check if upload was successful (response has path attribute)
        if hasattr(res, 'path') and res.path:
            self.file_name = file.name
            self.file_path = unique_name
            self.save()
        else:
            raise Exception(f"Upload failed: {res}")

    def get_public_url(self):
        """
        Returns a public URL for the file.
        """
        if not self.file_path:
            return None
        return supabase.storage.from_(SUPABASE_BUCKET).get_public_url(self.file_path)

    def get_signed_url(self, expires_in=60):
        """
        Returns a signed temporary URL for the file (default: 60s).
        """
        if not self.file_path:
            return None
        res = supabase.storage.from_(SUPABASE_BUCKET).create_signed_url(self.file_path, expires_in)
        return res.get("signedURL", None)

    def delete_from_supabase(self):
        """
        Deletes file from Supabase storage.
        """
        if self.file_path:
            supabase.storage.from_(SUPABASE_BUCKET).remove([self.file_path])

