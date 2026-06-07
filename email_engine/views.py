from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import SMTPServer, EmailQueue
from .serializers import SMTPServerSerializer, EmailQueueSerializer
from .smtp_health import check_smtp_health
from .email_sender import send_single_email

class SMTPServerViewSet(viewsets.ModelViewSet):
    serializer_class = SMTPServerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return SMTPServer.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
  #  @action(detail=True, methods=['post'])
    def test_health(self, request, pk=None):
        smtp = self.get_object()
        is_healthy = check_smtp_health(smtp)
        return Response({'healthy': is_healthy})

class EmailQueueViewSet(viewsets.ModelViewSet):
    serializer_class = EmailQueueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return EmailQueue.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        email = self.get_object()
        if email.status in ['failed', 'retry'] and email.can_retry():
            email.status = 'pending'
            email.retry_count += 1
            email.save(update_fields=['status', 'retry_count'])
            # Optionally send immediately
            send_single_email(email)
            return Response({'status': 'retrying'})
        return Response({'error': 'Cannot retry'}, status=status.HTTP_400_BAD_REQUEST)