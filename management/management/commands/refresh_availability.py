from django.core.management.base import NoArgsCommand
from core.tasks import refresh_availability


class Command(NoArgsCommand):
    help = 'Refresh the database with the current lab and room availability'

    def handle_noargs(self, **options):
        refresh_availability()
