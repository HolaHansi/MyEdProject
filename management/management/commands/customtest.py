from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = 'test'

    def handle_noargs(self, **options):
        self.stdout.write('test command run')
