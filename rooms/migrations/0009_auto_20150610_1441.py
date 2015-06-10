# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0008_auto_20150610_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookable_room',
            name='id',
            field=models.IntegerField(default=None, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='building_feed',
            name='id',
            field=models.IntegerField(default=None, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room_feed',
            name='id',
            field=models.IntegerField(default=None, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bookable_room',
            name='key',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='building_feed',
            name='key',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='room_feed',
            name='key',
            field=models.IntegerField(),
        ),
    ]
