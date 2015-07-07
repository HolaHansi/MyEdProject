from .base import *

# debugging should be on in development - NEVER in production!
DEBUG = True

# This variable is used in views to check whether the app is running in development or production.
ENV_TYPE = 'development'

# Database for development - SQLite
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

STATIC_ROOT = 'staticfiles'
