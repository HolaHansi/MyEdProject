# This file is run by a Cron job every 24 hours

import os

# set up the django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.production")

from core.tasks import refresh_locations

refresh_locations()
