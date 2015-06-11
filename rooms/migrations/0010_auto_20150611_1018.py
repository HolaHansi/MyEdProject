# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0009_auto_20150610_1441'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bookable_room',
            old_name='key',
            new_name='abbreviation',
        ),
        migrations.RenameField(
            model_name='building_feed',
            old_name='key',
            new_name='abbreviation',
        ),
        migrations.RenameField(
            model_name='room_feed',
            old_name='key',
            new_name='abbreviation',
        ),
        migrations.AddField(
            model_name='building_feed',
            name='name',
            field=models.CharField(default='john', max_length=100),
            preserve_default=False,
        ),
    ]
