from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.conf import settings
class User(AbstractUser):
    company_name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username
    




class SMTPSetting(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    smtp_host = models.CharField(
        max_length=255
    )

    smtp_port = models.IntegerField(
        default=587
    )

    smtp_username = models.CharField(
        max_length=255
    )

    smtp_password = models.CharField(
        max_length=255
    )

    use_tls = models.BooleanField(
        default=True
    )

    from_email = models.EmailField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.user.username