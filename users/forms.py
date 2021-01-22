from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from .models import Contact

User = get_user_model()


class CreationForm(UserCreationForm):
    model = User
    fields = ('first_name', 'last_name', 'username', 'email')


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'body')
