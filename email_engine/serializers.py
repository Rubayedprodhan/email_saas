from rest_framework import serializers
from .models import SMTPServer, EmailQueue

class SMTPServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPServer
        exclude = ['user', 'password', 'consecutive_failures', 'sent_today']
        read_only_fields = ['status', 'health_check_passed', 'last_health_check', 'last_used']
    
    def create(self, validated_data):
        # Hash password? For now store as plain. Better to encrypt using django-fernet-fields.
        return super().create(validated_data)

class EmailQueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailQueue
        exclude = ['user', 'retry_count', 'last_error', 'smtp_server']
        read_only_fields = ['uuid', 'status', 'sent_at', 'created_at']