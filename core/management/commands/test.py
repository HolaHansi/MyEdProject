from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'test'

    def handle(self, *args, **options):
        print('test command run')