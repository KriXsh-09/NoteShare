from django import forms
from .models import Note
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class NoteForm(forms.ModelForm):
	class Meta:
		model = Note
		fields = ['title', 'description', 'file']



class RegisterForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']