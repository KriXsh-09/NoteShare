from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
	list_display = ('title', 'uploaded_by', 'uploaded_at')
	search_fields = ('title', 'description', 'uploaded_by__username')