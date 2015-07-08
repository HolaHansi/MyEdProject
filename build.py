import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

from django.core.management import execute_from_command_line
from core.tasks import repopulate_all_tables

execute_from_command_line(['manage.py','makemigrations'])
execute_from_command_line(['manage.py','migrate'])
print('Successfully migrated')
repopulate_all_tables()
print('Database successfully built')
