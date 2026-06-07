# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    workspace_name = models.CharField(max_length=100, default='Default Workspace')
    
    # Verification
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=255, blank=True)
    password_reset_token = models.CharField(max_length=255, blank=True)
    password_reset_token_created_at = models.DateTimeField(null=True, blank=True)
    
    # Limits
    monthly_email_limit = models.IntegerField(default=10000)
    email_sent_this_month = models.IntegerField(default=0)
    last_reset_date = models.DateField(default=timezone.now)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def generate_verification_token(self):
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.save(update_fields=['email_verification_token'])
        return token
    
    def generate_password_reset_token(self):
        token = secrets.token_urlsafe(32)
        self.password_reset_token = token
        self.password_reset_token_created_at = timezone.now()
        self.save(update_fields=['password_reset_token', 'password_reset_token_created_at'])
        return token
    
    def is_password_reset_token_valid(self):
        if not self.password_reset_token_created_at:
            return False
        expiry_time = self.password_reset_token_created_at + timezone.timedelta(hours=24)
        return timezone.now() <= expiry_time
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'users'