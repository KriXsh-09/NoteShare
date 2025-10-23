from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Note, DEFAULT_SIGNED_URL_EXPIRY
from .forms import NoteForm, RegisterForm
import requests
import logging

logger = logging.getLogger(__name__)

# Constants
RECENT_NOTES_COUNT = 6
PAGINATION_SIZE = 10


# Helper functions
def _get_signed_url_for_note(note, expires_in=DEFAULT_SIGNED_URL_EXPIRY):
    """Helper function to get signed URL for a note with error handling"""
    if not note.file_path:
        return None, "File not available."
    
    signed_url = note.get_signed_url(expires_in)
    if not signed_url:
        return None, "Could not generate signed URL."
    
    return signed_url, None

def _create_file_response(content, filename, content_type='application/octet-stream', disposition='attachment'):
    """Helper function to create Django response with proper headers"""
    response = HttpResponse(content)
    response['Content-Type'] = content_type
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    response['Content-Length'] = str(len(content))
    return response

def _fetch_file_from_url(url, error_message="Failed to fetch file"):
    """Helper function to fetch file from URL with error handling"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content, None
    except requests.RequestException as e:
        logger.error(f"{error_message}: {e}")
        return None, f"{error_message}: {e}"


# ------------------ DOWNLOAD VIEW ------------------

@login_required
def download_note(request, note_id):
    """
    Downloads file from Supabase with proper headers.
    """
    note = get_object_or_404(Note, id=note_id)

    # Get signed URL
    signed_url, error = _get_signed_url_for_note(note)
    if error:
        messages.error(request, error)
        return redirect('notes:home')

    # Fetch file content
    content, error = _fetch_file_from_url(signed_url, "Download failed")
    if error:
        messages.error(request, error)
        return redirect('notes:home')

    # Determine content type
    content_type = 'application/pdf' if note.is_pdf else 'application/octet-stream'
    
    # Create response with proper headers
    return _create_file_response(content, note.file_name, content_type, 'attachment')


# ------------------ PREVIEW VIEW ------------------

@login_required
def view_note(request, note_id):
    """
    Generates a signed Supabase URL for preview.
    Works for images, PDFs, videos, etc.
    """
    note = get_object_or_404(Note, id=note_id)

    # Get signed URL
    signed_url, error = _get_signed_url_for_note(note)
    if error:
        messages.error(request, error)
        return redirect('notes:home')

    # For PDFs, fetch and serve with proper headers for inline viewing
    if note.is_pdf:
        content, error = _fetch_file_from_url(signed_url, "Preview failed")
        if error:
            messages.error(request, error)
            return redirect('notes:home')
        
        return _create_file_response(content, note.file_name, 'application/pdf', 'inline')

    return render(request, 'notes/view_note.html', {'file_url': signed_url, 'note': note})


def index(request):
    return render(request, 'notes/index.html')


@login_required
def home(request):
    """Display recent notes and all notes with pagination"""
    recent = Note.objects.order_by('-uploaded_at')[:RECENT_NOTES_COUNT]
    all_notes = Note.objects.order_by('-uploaded_at')
    
    # Add pagination for all notes
    paginator = Paginator(all_notes, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notes/home.html', {
        'recent': recent, 
        'all_notes': page_obj,
        'page_obj': page_obj
    })


@login_required
def my_upload(request):
    """Display user's uploaded notes with pagination"""
    notes = Note.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    
    # Add pagination
    paginator = Paginator(notes, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notes/my_upload.html', {'notes': page_obj, 'page_obj': page_obj})


# ------------------ DELETE VIEW ------------------

@login_required
def delete_note(request, note_id):
    """Delete a note and its associated file from Supabase"""
    note = get_object_or_404(Note, id=note_id, uploaded_by=request.user)

    if request.method == "POST":
        try:
            # Delete from Supabase first
            note.delete_from_supabase()
            # Then delete from database
            note.delete()
            messages.success(request, "Note deleted successfully.")
            logger.info(f"Note {note_id} deleted by user {request.user.username}")
        except Exception as e:
            logger.error(f"Error deleting note {note_id}: {e}")
            messages.error(request, f"Error deleting note: {e}")
        return redirect('notes:my_upload')

    messages.error(request, "Invalid request.")
    return redirect('notes:my_upload')


# ------------------ UPLOAD VIEW ------------------

@login_required
def upload(request):
    """Handle note upload with file validation"""
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.uploaded_by = request.user
            
            # Upload file to Supabase first
            file = request.FILES.get('file')
            if file:
                try:
                    # Upload to Supabase before saving to database
                    note.upload_to_supabase(file)
                    messages.success(request, 'Note uploaded successfully.')
                    logger.info(f"Note '{note.title}' uploaded by user {request.user.username}")
                    return redirect('notes:my_upload')
                except Exception as e:
                    logger.error(f"Upload failed for user {request.user.username}: {e}")
                    messages.error(request, f"Upload failed: {e}")
                    return render(request, 'notes/upload.html', {'form': form})
            else:
                messages.error(request, 'No file provided.')
                return render(request, 'notes/upload.html', {'form': form})
        else:
            logger.warning(f"Form validation failed for user {request.user.username}: {form.errors}")
            messages.error(request, f"Form validation failed: {form.errors}")
    else:
        form = NoteForm()
    
    return render(request, 'notes/upload.html', {'form': form})


# ------------------ AUTH & SEARCH ------------------

def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"New user registered: {user.username}")
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('notes:login')
        else:
            logger.warning(f"Registration failed: {form.errors}")
    else:
        form = RegisterForm()
    
    return render(request, 'notes/register.html', {'form': form})


def login(request):
    """Display login page"""
    return render(request, 'notes/login.html')


def search_notes(request):
    """Search notes by title with improved query handling"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        results = []
    else:
        # Search in both title and description
        results = Note.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('-uploaded_at')
        
        # Add pagination for search results
        paginator = Paginator(results, PAGINATION_SIZE)
        page_number = request.GET.get('page')
        results = paginator.get_page(page_number)
    
    return render(request, 'notes/search_result.html', {
        'query': query,
        'results': results,
        'page_obj': results if hasattr(results, 'has_other_pages') else None
    })
