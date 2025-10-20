from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from cloudinary.utils import cloudinary_url
from .models import Note
from .forms import NoteForm, RegisterForm
from django.contrib import messages
import cloudinary.uploader

# ------------------ DOWNLOAD VIEW ------------------

@login_required
def download_note(request, note_id):
    """
    Generates a signed Cloudinary URL for secure download
    and redirects the user to it.
    """
    note = get_object_or_404(Note, id=note_id)

    if not note.file:
        messages.error(request, "File not available.")
        return render(request, 'notes/home.html', {'recent': recent, 'all_notes': all_notes})

    # Generate signed URL valid for 1 minute (adjust as needed)
    url, options = cloudinary_url(
        note.file.public_id,
        resource_type='auto',
        type='authenticated',  # Use 'private' for signed URLs
        sign_url=True,
        expires_at=60
    )
    return HttpResponseRedirect(url)


# ------------------ PREVIEW VIEW ------------------

@login_required
def view_note(request, note_id):
    """
    Generates a signed Cloudinary URL for preview.
    Works for images, PDFs, videos, etc.
    """
    note = get_object_or_404(Note, id=note_id)

    if not note.file:
        messages.error(request, "File not available.")
        return render(request, 'notes/home.html', {'recent': recent, 'all_notes': all_notes})

    # Signed URL for preview, valid for 1 minute
    url, options = cloudinary_url(
        note.file.public_id,
        resource_type='auto',
        type='authenticated',
        sign_url=True,
        expires_at=60
    )

    return render(request, 'notes/view_note.html', {'file_url': url, 'note': note})


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

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, uploaded_by=request.user)

    if request.method == "POST":
        # Delete file from Cloudinary if it exists
        if note.file:
            try:
                # Safely get public_id from the Cloudinary field
                public_id = getattr(note.file, "public_id", None)
                if public_id:
                    cloudinary.uploader.destroy(public_id)
            except Exception as e:
                print(f"Cloudinary deletion error: {e}")

        # Delete the database record
        note.delete()

        messages.success(request, "Note deleted successfully.")
        return redirect('notes:my_upload')
    else:
        messages.error(request, "Invalid request.")
        return redirect('notes:my_upload')



@login_required
def upload(request):
	if request.method == 'POST':
		form = NoteForm(request.POST, request.FILES)
		if form.is_valid():
			note = form.save(commit=False)
			note.uploaded_by = request.user
			note.save()
			messages.success(request, 'Note uploaded successfully.')
			return redirect('notes:my_upload')
	else:
		form = NoteForm()
	return render(request, 'notes/upload.html', {'form': form})


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

'''
def view_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    return render(request, 'notes/view_note.html', {'note': note})
'''
def search_notes(request):
    query = request.GET.get('q', '')
    results = Note.objects.filter(title__icontains=query) if query else []
    return render(request, 'notes/search_result.html', {
        'query': query,
        'results': results
    })

