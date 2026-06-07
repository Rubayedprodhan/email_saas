from django.core.management.base import BaseCommand
#from email_engine.email_sender import process_queue
from email_engine.email_sender import process_queue
class Command(BaseCommand):
    help = 'Process pending emails in the queue'
    
    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=50, help='Number of emails to process')
    
    def handle(self, *args, **options):
        limit = options['limit']
        count = process_queue(limit=limit)
        self.stdout.write(self.style.SUCCESS(f'Processed {count} emails'))