# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0005_auto_20150610_1115'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookable_Room',
            fields=[
                ('key', models.IntegerField(serialize=False, primary_key=True)),
                ('field_building_name', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('capacity', models.IntegerField(default=0)),
                ('pc', models.BooleanField(default=False)),
                ('projector', models.BooleanField(default=False)),
                ('whiteboard', models.BooleanField(default=False)),
                ('blackboard', models.BooleanField(default=False)),
                ('longitude', models.FloatField()),
                ('latitude', models.FloatField()),
            ],
        ),
    ]
