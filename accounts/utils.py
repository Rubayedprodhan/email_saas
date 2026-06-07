# accounts/utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_verification_email(user, request):
    token = user.email_verification_token
    # Build verification link (frontend or backend URL)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    # Alternatively, you can use a backend endpoint:
    # verify_url = request.build_absolute_uri(reverse('accounts:verify-email') + f'?token={token}')
    
    subject = "Verify your email address"
    message = f"""
    Hi {user.username or user.email},
    
    Please click the link below to verify your email address:
    {verify_url}
    
    This link expires in 24 hours.
    
    Thank you,
    Email SaaS Team
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def send_password_reset_email(user, request):
    token = user.generate_password_reset_token()
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    subject = "Reset your password"
    message = f"""
    Hi {user.username or user.email},
    
    You requested a password reset. Click the link below to set a new password:
    {reset_url}
    
    This link expires in 24 hours.
    
    If you didn't request this, please ignore this email.
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])