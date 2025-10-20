
from django.shortcuts import render, redirect, get_object_or_404
from .models import Note
from .forms import NoteForm, RegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
import cloudinary.uploader


def view_note(request, note_id):
	note = get_object_or_404(Note, id=note_id)
	return render(request, 'notes/view_note.html', {'note': note})

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


def view_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    return render(request, 'notes/view_note.html', {'note': note})

def search_notes(request):
    query = request.GET.get('q', '')
    results = Note.objects.filter(title__icontains=query) if query else []
    return render(request, 'notes/search_result.html', {
        'query': query,
        'results': results
    })

