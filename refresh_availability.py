# This file is run by a Cron job every 24 hours

import os
import django

# set up the django environment
django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.production")

from core.tasks import refresh_availability

refresh_availability()
