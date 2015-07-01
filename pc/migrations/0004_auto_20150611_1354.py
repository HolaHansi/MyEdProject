# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pc', '0003_auto_20150611_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='pc_space',
            name='latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='pc_space',
            name='longitude',
            field=models.FloatField(default=0),
        ),
    ]
