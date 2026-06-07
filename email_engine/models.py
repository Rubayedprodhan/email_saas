# email_engine/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class SMTPServer(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('failed', 'Failed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='smtp_servers')
    name = models.CharField(max_length=100, help_text="e.g., SendGrid Primary")
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField(default=587)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    from_email = models.EmailField()
    from_name = models.CharField(max_length=255, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    priority = models.PositiveSmallIntegerField(default=100)
    last_used = models.DateTimeField(null=True, blank=True)
    last_health_check = models.DateTimeField(null=True, blank=True)
    health_check_passed = models.BooleanField(default=True)
    consecutive_failures = models.PositiveIntegerField(default=0)
    
    # আপনি connection_failure_message চাইলে যোগ করতে পারেন
    connection_failure_message = models.CharField(max_length=200, blank=True)
    
    daily_limit = models.PositiveIntegerField(default=0)
    sent_today = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.host})"

class EmailQueue(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('retry', 'Retry'),
    )
    PRIORITY_CHOICES = (
        (1, 'High'),
        (2, 'Normal'),
        (3, 'Low'),
    )
    
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_queue')
    
    # কমেন্ট করুন অথবা রাখুন - এখন campaigns.Campaign আছে
    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.SET_NULL, null=True, blank=True, related_name='emails')
    
    to_email = models.EmailField()
    to_name = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=998)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=2)
    scheduled_at = models.DateTimeField(default=timezone.now)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    retry_count = models.PositiveSmallIntegerField(default=0)
    max_retries = models.PositiveSmallIntegerField(default=3)
    last_error = models.TextField(blank=True)
    
    smtp_server = models.ForeignKey(SMTPServer, on_delete=models.SET_NULL, null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    inline_images = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.subject} -> {self.to_email}"