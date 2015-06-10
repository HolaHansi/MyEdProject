# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_auto_20150610_1003'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookableroom',
            name='blackboard',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bookableroom',
            name='pc',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bookableroom',
            name='projector',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='bookableroom',
            name='whiteboard',
            field=models.BooleanField(default=False),
        ),
    ]
