from django.core.management.base import NoArgsCommand
from core.tasks import refresh_locations


class Command(NoArgsCommand):
    help = 'Check for any changed labs or rooms'

    def handle_noargs(self, **options):
        refresh_locations()
