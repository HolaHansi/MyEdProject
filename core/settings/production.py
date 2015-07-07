from .base import *

# Debug off in production
DEBUG = True

# this needs to be specified, when debug is off.
ALLOWED_HOSTS = ['.book.is.ed.ac.uk']

#This variable is used in views to check whether the app is running in development or production.
ENV_TYPE = 'production'



# USE Mysql in production - baseconfig.cnf contains all the configurations of the db on the chostt.
DATABASES = {
        'default': {
                'ENGINE': 'django.db.backends.mysql',

                'OPTIONS': {
                        'read_default_file': os.path.join(BASE_DIR, 'databaseconfig.cnf')
                }
        }
}



#STATIC_ROOT holds the path to where django will put all the collected staticfiles,
# after runnning the command ./manage.py collectstatic.

STATIC_ROOT = os.path.join(BASE_DIR, '../public_html/staticfiles')

