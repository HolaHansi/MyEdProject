#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # remember to update settings to .production in production!
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'core.settings.development')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
