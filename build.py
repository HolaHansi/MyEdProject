"""
Calling this module will set up the django database, apply migrations and populate the tables.
Should be called like this : python build.py, and on the apache server: python3 build.py
"""
import os


# set up the django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")

from django.core.management import execute_from_command_line
from core.tasks import repopulate_all_tables

# check for changes to the database structure
execute_from_command_line(['manage.py', 'makemigrations'])
# change the structure of the database if necessary
execute_from_command_line(['manage.py', 'migrate'])
print('Successfully migrated')

# populate the database
repopulate_all_tables()

print('Database successfully built')
