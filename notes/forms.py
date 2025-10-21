from django import forms
from .models import Note
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class NoteForm(forms.ModelForm):
	file = forms.FileField(required=True, widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.pptx,.xlsx'}))
	
	class Meta:
		model = Note
		fields = ['title', 'description']
		widgets = {
			'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter note title'}),
			'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter note description', 'rows': 3}),
		}



class RegisterForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']