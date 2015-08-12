# This file is run by a Cron job every 24 hours

import django
from django.conf import settings
from core.settings import production

settings.configure(default_settings=production)
django.setup()

# Now this script can use any part of Django it needs.

from core.tasks import refresh_availability

refresh_availability()
