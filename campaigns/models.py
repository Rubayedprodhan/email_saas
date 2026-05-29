from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField

class EmailTemplate(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=255
    )

    html_content = RichTextField()

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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    subject = models.CharField(max_length=255)

    message = models.TextField()

    template = models.ForeignKey(EmailTemplate,on_delete=models.SET_NULL,null=True,blank=True)

    scheduled_time = models.DateTimeField(null=True,blank=True)

    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='draft')

    created_at = models.DateTimeField(auto_now_add=True)

    is_ab_test = models.BooleanField(default=False)

    variant_a_subject = models.CharField(max_length=255, blank=True, null=True)
    variant_b_subject = models.CharField(max_length=255, blank=True, null=True)

    variant_a_message = models.TextField(blank=True, null=True)
    variant_b_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.subject


class EmailTrack(models.Model):

    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE )

    email = models.EmailField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default='sent')

    error_message = models.TextField(blank=True,null=True)

    opened = models.BooleanField(default=False)

    opened_at = models.DateTimeField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class ClickTrack(models.Model):

    campaign = models.ForeignKey(Campaign,on_delete=models.CASCADE)

    email = models.EmailField()

    original_url = models.URLField()

    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



class MediaFile(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    file = models.ImageField( upload_to='uploads/')

    created_at = models.DateTimeField(auto_now_add=True )

    def __str__(self):

        return self.file.url



class EmailBlock(models.Model):

    BLOCK_TYPES = (

        ('heading', 'Heading'),

        ('text', 'Text'),

        ('button', 'Button'),

        ('image', 'Image'),
    )

    template = models.ForeignKey(EmailTemplate,on_delete=models.CASCADE,related_name='blocks')

    block_type = models.CharField(max_length=50,choices=BLOCK_TYPES)

    content = models.TextField()

    sort_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:

        ordering = ['sort_order']

    def __str__(self):

        return self.block_type


class SavedSection(models.Model):

    BLOCK_TYPES = (

        ('heading', 'Heading'),

        ('text', 'Text'),

        ('button', 'Button'),

        ('image', 'Image'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)

    name = models.CharField(max_length=255)

    block_type = models.CharField(max_length=50,choices=BLOCK_TYPES)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.name


class EmailBlockHistory(models.Model):

    ACTION_TYPES = (

        ('update', 'Update'),

        ('delete', 'Delete'),

        ('create', 'Create'),
    )

    block = models.ForeignKey( EmailBlock,on_delete=models.CASCADE, related_name='history')

    content = models.TextField()

    action_type = models.CharField(max_length=50,choices=ACTION_TYPES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.action_type


class ABTestResult(models.Model):

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)

    variant = models.CharField(max_length=1)  # A or B

    email = models.EmailField()

    opened = models.BooleanField(default=False)

    clicked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)