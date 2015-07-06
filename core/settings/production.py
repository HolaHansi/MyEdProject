from .base import *

# Debug off in production
DEBUG = False

# this needs to be specified, when debug is off.
ALLOWED_HOSTS = ['.book.is.ed.ac.uk']

#This variable is used in views to check whether the app is running in development or production.
ENV_TYPE = 'production'

# USE Mysql in production - configured for a specific db on the chostt.
DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.mysql',

                'OPTIONS': {
                        'read_default_file': os.path.join(BASE_DIR, 'databaseconfig.cnf')
                }
        }
}

STATIC_ROOT = os.path.join(BASE_DIR, '../public_html/staticfiles')

