from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from .models import Note
from .forms import NoteForm, RegisterForm
import requests


# ------------------ DOWNLOAD VIEW ------------------

@login_required
def download_note(request, note_id):
    """
    Downloads file from Supabase with proper headers.
    """
    note = get_object_or_404(Note, id=note_id)

    if not note.file_path:
        messages.error(request, "File not available.")
        return redirect('notes:home')

    # Get signed URL
    signed_url = note.get_signed_url(60)
    if not signed_url:
        messages.error(request, "Could not generate signed URL.")
        return redirect('notes:home')

    try:
        # Fetch file from Supabase
        response = requests.get(signed_url)
        response.raise_for_status()
        
        # Create Django response with proper headers
        django_response = HttpResponse(response.content)
        django_response['Content-Type'] = 'application/pdf' if note.file_name.lower().endswith('.pdf') else 'application/octet-stream'
        django_response['Content-Disposition'] = f'attachment; filename="{note.file_name}"'
        django_response['Content-Length'] = str(len(response.content))
        
        return django_response
        
    except requests.RequestException as e:
        messages.error(request, f"Download failed: {e}")
        return redirect('notes:home')


# ------------------ PREVIEW VIEW ------------------

@login_required
def view_note(request, note_id):
    """
    Generates a signed Supabase URL for preview.
    Works for images, PDFs, videos, etc.
    """
    note = get_object_or_404(Note, id=note_id)

    if not note.file_path:
        messages.error(request, "File not available.")
        return redirect('notes:home')

    signed_url = note.get_signed_url(60)
    if not signed_url:
        messages.error(request, "Could not generate preview URL.")
        return redirect('notes:home')

    # For PDFs, fetch and serve with proper headers for inline viewing
    if note.file_name and note.file_name.lower().endswith('.pdf'):
        try:
            response = requests.get(signed_url)
            response.raise_for_status()
            
            # Create Django response with proper headers for inline viewing
            django_response = HttpResponse(response.content)
            django_response['Content-Type'] = 'application/pdf'
            django_response['Content-Disposition'] = f'inline; filename="{note.file_name}"'
            django_response['Content-Length'] = str(len(response.content))
            
            return django_response
            
        except requests.RequestException as e:
            messages.error(request, f"Preview failed: {e}")
            return redirect('notes:home')

    return render(request, 'notes/view_note.html', {'file_url': signed_url, 'note': note})


def index(request):
    return render(request, 'notes/index.html')


@login_required
def home(request):
    recent = Note.objects.order_by('-uploaded_at')[:6]
    all_notes = Note.objects.order_by('-uploaded_at')
    return render(request, 'notes/home.html', {'recent': recent, 'all_notes': all_notes})


@login_required
def my_upload(request):
    qs = Note.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    return render(request, 'notes/my_upload.html', {'notes': qs})


# ------------------ DELETE VIEW ------------------

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, uploaded_by=request.user)

    if request.method == "POST":
        try:
            note.delete_from_supabase()
            note.delete()
            messages.success(request, "Note deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting note: {e}")
        return redirect('notes:my_upload')

    messages.error(request, "Invalid request.")
    return redirect('notes:my_upload')


# ------------------ UPLOAD VIEW ------------------

@login_required
def upload(request):
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
                except Exception as e:
                    messages.error(request, f"Upload failed: {e}")
                    return render(request, 'notes/upload.html', {'form': form})
            else:
                messages.error(request, 'No file provided.')
                return render(request, 'notes/upload.html', {'form': form})
            
            return redirect('notes:my_upload')
        else:
            messages.error(request, f"Form validation failed: {form.errors}")
    else:
        form = NoteForm()
    return render(request, 'notes/upload.html', {'form': form})


# ------------------ AUTH & SEARCH ------------------

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('notes:login')
    else:
        form = RegisterForm()
    return render(request, 'notes/register.html', {'form': form})


def login(request):
    return render(request, 'notes/login.html')


def search_notes(request):
    query = request.GET.get('q', '')
    results = Note.objects.filter(title__icontains=query) if query else []
    return render(request, 'notes/search_result.html', {
        'query': query,
        'results': results
    })
