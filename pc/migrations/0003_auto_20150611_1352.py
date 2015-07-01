# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pc', '0002_room_ratio'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Room',
            new_name='PC_Space',
        ),
    ]
