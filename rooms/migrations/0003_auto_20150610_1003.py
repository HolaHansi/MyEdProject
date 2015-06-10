# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_auto_20150609_1540'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookableroom',
            name='id',
        ),
        migrations.RemoveField(
            model_name='webproxy',
            name='id',
        ),
        migrations.AlterField(
            model_name='bookableroom',
            name='key',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='webproxy',
            name='key',
            field=models.IntegerField(serialize=False, primary_key=True),
        ),
    ]
