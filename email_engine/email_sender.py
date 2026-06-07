import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from django.conf import settings
from django.utils import timezone
from email_engine.models import EmailQueue, SMTPServer
from email_engine.smtp_health import check_smtp_health, get_available_smtp

def send_single_email(queue_item: EmailQueue) -> bool:
    """
    Actually send one email using the selected SMTP.
    Updates queue item status.
    """
    smtp = queue_item.smtp_server
    if not smtp or not smtp.can_send():
        # Try to get new SMTP
        smtp = get_available_smtp(queue_item.user)
        if not smtp:
            queue_item.status = 'failed'
            queue_item.last_error = "No available SMTP server"
            queue_item.save(update_fields=['status', 'last_error'])
            return False
        queue_item.smtp_server = smtp
        queue_item.save(update_fields=['smtp_server'])
    
    # Build email
    msg = MIMEMultipart('alternative')
    msg['Subject'] = queue_item.subject
    from_addr = f"{smtp.from_name} <{smtp.from_email}>" if smtp.from_name else smtp.from_email
    msg['From'] = from_addr
    msg['To'] = queue_item.to_email
    if queue_item.to_name:
        msg['To'] = f"{queue_item.to_name} <{queue_item.to_email}>"
    
    # Attach plain text and HTML
    if queue_item.text_content:
        part_text = MIMEText(queue_item.text_content, 'plain')
        msg.attach(part_text)
    part_html = MIMEText(queue_item.html_content, 'html')
    msg.attach(part_html)
    
    # Attachments
    for attachment in queue_item.attachments:
        file_path = attachment.get('path')
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{attachment["name"]}"')
                msg.attach(part)
    
    # Inline images (for HTML)
    for inline in queue_item.inline_images:
        cid = inline.get('cid')
        file_path = inline.get('path')
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                part = MIMEBase('image', 'png')  # detect mime better
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-ID', f'<{cid}>')
                part.add_header('Content-Disposition', 'inline')
                msg.attach(part)
    
    # Send
    try:
        if smtp.use_ssl:
            server = smtplib.SMTP_SSL(smtp.host, smtp.port, timeout=30)
        else:
            server = smtplib.SMTP(smtp.host, smtp.port, timeout=30)
            if smtp.use_tls:
                server.starttls()
        
        server.login(smtp.username, smtp.password)
        server.sendmail(smtp.from_email, [queue_item.to_email], msg.as_string())
        server.quit()
        
        # Update success
        queue_item.status = 'sent'
        queue_item.sent_at = timezone.now()
        queue_item.last_error = ''
        queue_item.save(update_fields=['status', 'sent_at', 'last_error'])
        smtp.mark_success()
        smtp.increment_sent_today()
        return True
    except Exception as e:
        queue_item.last_error = str(e)
        queue_item.retry_count += 1
        if queue_item.can_retry():
            queue_item.status = 'retry'
            # Exponential backoff: reschedule after 2^retry minutes
            delay = 2 ** queue_item.retry_count * 60
            queue_item.scheduled_at = timezone.now() + timezone.timedelta(seconds=delay)
        else:
            queue_item.status = 'failed'
        queue_item.save(update_fields=['status', 'last_error', 'retry_count', 'scheduled_at'])
        smtp.mark_failure()
        return False

def process_queue(limit=50):
    """Process pending email queue items."""
    pending = EmailQueue.objects.filter(
        status__in=['pending', 'retry'],
        scheduled_at__lte=timezone.now()
    ).select_related('user', 'smtp_server')[:limit]
    
    for item in pending:
        # Mark as sending to avoid duplicate processing
        if item.status != 'retry':
            item.status = 'sending'
            item.save(update_fields=['status'])
        send_single_email(item)
    
    return len(pending)