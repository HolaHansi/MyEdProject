# This file is run by a Cron job every 24 hours

from core.tasks import refresh_availability
import os

# set up the django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.production")

refresh_availability()
