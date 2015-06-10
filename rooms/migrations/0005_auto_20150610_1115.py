# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_auto_20150610_1026'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Webproxy',
            new_name='Building_Feed',
        ),
        migrations.RenameModel(
            old_name='BookableRoom',
            new_name='Room_Feed',
        ),
    ]
