from django.db import models
from django.conf import settings


class EmailTemplate(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    html_content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class Campaign(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    subject = models.CharField(
        max_length=255
    )

    message = models.TextField()

    template = models.ForeignKey(
        'EmailTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    scheduled_time = models.DateTimeField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.subject


class EmailTrack(models.Model):

    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE
    )

    email = models.EmailField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent'
    )

    error_message = models.TextField(
        blank=True,
        null=True
    )

    opened = models.BooleanField(
        default=False
    )

    opened_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email


class ClickTrack(models.Model):

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE
    )

    email = models.EmailField()

    original_url = models.URLField()

    clicked_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email