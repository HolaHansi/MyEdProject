# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('field_building_name', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=200)),
                ('capacity', models.IntegerField(default=0)),
                ('building_host_key', models.IntegerField()),
                ('projector', models.BooleanField()),
                ('dvd', models.BooleanField()),
                ('induction_loop', models.BooleanField()),
                ('laptop_connectivity', models.BooleanField()),
                ('ohp', models.BooleanField()),
                ('pa', models.BooleanField()),
                ('pc', models.BooleanField()),
                ('prs_system', models.BooleanField()),
                ('vcr', models.BooleanField()),
                ('visualizer', models.BooleanField()),
                ('whiteboard', models.BooleanField()),
                ('blackboard', models.BooleanField()),
                ('lcd_display', models.BooleanField()),
                ('webcam', models.BooleanField()),
                ('smartboard', models.BooleanField()),
                ('usb_conference_table_mic', models.BooleanField()),
                ('wheelchair_accessible', models.BooleanField()),
                ('control_system', models.BooleanField()),
                ('stereo_audio_system', models.BooleanField()),
                ('fm_induction_system', models.BooleanField()),
                ('writing_tablet', models.BooleanField()),
                ('compact_flash_recorder', models.BooleanField()),
                ('lecture_capture', models.BooleanField()),
                ('infrared_hearing_helper', models.BooleanField()),
                ('plasma_screen', models.BooleanField()),
            ],
        ),
    ]
