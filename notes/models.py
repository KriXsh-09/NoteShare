from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Note(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = CloudinaryField('file', resource_type='auto', folder='Notes_uploaded/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # If the uploaded file is PDF, force resource_type='raw'
        if self.file and str(self.file).endswith('.pdf'):
            self.file.resource_type = 'raw'
        super().save(*args, **kwargs)
