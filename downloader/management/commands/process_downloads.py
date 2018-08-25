from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Periodically checks for new upload jobs and runs them.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        