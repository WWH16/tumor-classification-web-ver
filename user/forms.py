from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class SignupForm(UserCreationForm):
    employee_id = forms.CharField(max_length=20, required=True, label="Employee ID")
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta:
        model = User
        fields = ("employee_id", "first_name", "last_name", "email", "password1", "password2")

class LoginForm(forms.Form):
    employee_id = forms.CharField(max_length=20, required=True, label="Employee ID")
    password = forms.CharField(widget=forms.PasswordInput, required=True)
