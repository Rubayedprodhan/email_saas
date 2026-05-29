from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

from .models import SMTPSetting
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'company_name',
            'password1',
            'password2'
        ]




class SMTPSettingForm(forms.ModelForm):

    class Meta:

        model = SMTPSetting

        fields = [
            'smtp_host',
            'smtp_port',
            'smtp_username',
            'smtp_password',
            'use_tls',
            'from_email'
        ]

        widgets = {

            'smtp_host': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'smtp_port': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'smtp_username': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'smtp_password': forms.PasswordInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'from_email': forms.EmailInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }