from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Campaign(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    subject = models.CharField(max_length=255)

    message = models.TextField()

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