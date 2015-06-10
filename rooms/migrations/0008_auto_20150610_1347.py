# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0007_auto_20150610_1312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room_feed',
            name='latitude',
        ),
        migrations.RemoveField(
            model_name='room_feed',
            name='longitude',
        ),
    ]
