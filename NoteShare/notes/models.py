from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	file = models.FileField(upload_to='notes_files/')
	uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.title} - {self.uploaded_by.username}"