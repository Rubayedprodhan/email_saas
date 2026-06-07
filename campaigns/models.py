from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class Campaign(models.Model):
    """Temporary model for Phase 3. Will be expanded in Phase 4."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name