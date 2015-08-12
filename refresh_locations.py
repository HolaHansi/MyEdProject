# This file is run by a Cron job every 24 hours

from core.tasks import refresh_locations

refresh_locations()
