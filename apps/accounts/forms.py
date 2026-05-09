from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

# class CustomRegistrationForm(UserCreationForm):
#     class Meta:
#         model=CustomUser
#         # Add the fields you want user to fill
#         fields= ['email',]