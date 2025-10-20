from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Note(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = CloudinaryField('file', resource_type='auto', folder='Notes_uploaded/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.uploaded_by.username}"
