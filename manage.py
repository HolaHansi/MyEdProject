#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # change settings to production on the server!
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
