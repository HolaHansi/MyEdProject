from django import forms
from .models import Entry, UserProfile
from django.contrib.auth.models import User


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['title', 'text']

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['is_a_john']



