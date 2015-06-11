# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0011_auto_20150611_1026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookable_room',
            name='abbreviation',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='building_feed',
            name='abbreviation',
            field=models.CharField(primary_key=True, max_length=30, serialize=False),
        ),
        migrations.AlterField(
            model_name='room_feed',
            name='abbreviation',
            field=models.CharField(max_length=30),
        ),
    ]
