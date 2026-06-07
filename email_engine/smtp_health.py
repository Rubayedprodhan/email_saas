import smtplib
from email.mime.text import MIMEText
from django.utils import timezone
from email_engine.models import SMTPServer

def check_smtp_health(smtp_server: SMTPServer) -> bool:
    """Test SMTP connection and login."""
    try:
        if smtp_server.use_ssl:
            server = smtplib.SMTP_SSL(smtp_server.host, smtp_server.port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_server.host, smtp_server.port, timeout=10)
            if smtp_server.use_tls:
                server.starttls()
        
        server.login(smtp_server.username, smtp_server.password)
        server.quit()
        
        smtp_server.health_check_passed = True
        smtp_server.last_health_check = timezone.now()
        smtp_server.save(update_fields=['health_check_passed', 'last_health_check'])
        return True
    except Exception as e:
        smtp_server.health_check_passed = False
        smtp_server.last_health_check = timezone.now()
        smtp_server.status = 'failed'
        smtp_server.save(update_fields=['health_check_passed', 'last_health_check', 'status'])
        return False

def get_available_smtp(user, preferred_smtp_id=None):
    """
    Returns the best available SMTP for a user.
    Implements rotation: picks lowest priority, least recently used, and healthy.
    """
    qs = SMTPServer.objects.filter(user=user, status='active', health_check_passed=True)
    if preferred_smtp_id:
        try:
            preferred = qs.get(id=preferred_smtp_id)
            if preferred.can_send():
                return preferred
        except SMTPServer.DoesNotExist:
            pass
    
    # Order by priority (lower first), then last_used (nulls first to give fresh ones chance)
    smtp = qs.order_by('priority', 'last_used').first()
    if smtp and smtp.can_send():
        return smtp
    return None