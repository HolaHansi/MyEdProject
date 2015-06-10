# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('location', models.CharField(serialize=False, max_length=200, primary_key=True)),
                ('free', models.IntegerField(default=0)),
                ('seats', models.IntegerField(default=0)),
                ('group', models.CharField(max_length=200)),
            ],
        ),
    ]
