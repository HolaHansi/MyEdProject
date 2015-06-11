from __future__ import absolute_import
from django.conf import settings
import os
from celery import Celery
from datetime import timedelta

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyEd.settings')



app = Celery('InternProject')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# for performing API calls and updating db periodically.
CELERYBEAT_SCHEDULE = {
    'get_data_pc': {
        'task': 'pc.tasks.get_data',
        'schedule': timedelta(seconds=20)
    },
    'get_data_rooms': {
        'task': 'rooms.tasks.get_data',
        'schedule': timedelta(seconds=30)
    }
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))