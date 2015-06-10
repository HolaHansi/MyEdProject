# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0006_bookable_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='room_feed',
            name='latitude',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='room_feed',
            name='longitude',
            field=models.FloatField(default=0.0),
        ),
    ]
