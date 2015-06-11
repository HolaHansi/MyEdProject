# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0010_auto_20150611_1018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookable_room',
            name='id',
        ),
        migrations.RemoveField(
            model_name='building_feed',
            name='id',
        ),
        migrations.RemoveField(
            model_name='room_feed',
            name='id',
        ),
        migrations.AlterField(
            model_name='bookable_room',
            name='title',
            field=models.CharField(primary_key=True, max_length=200, serialize=False),
        ),
        migrations.AlterField(
            model_name='building_feed',
            name='abbreviation',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='room_feed',
            name='title',
            field=models.CharField(primary_key=True, max_length=200, serialize=False),
        ),
    ]
