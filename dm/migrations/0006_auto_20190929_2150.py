# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-09-29 18:50
from __future__ import unicode_literals

from django.db import migrations, models
import dm.models_shared


class Migration(migrations.Migration):

    dependencies = [
        ('dm', '0005_auto_20190929_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelx',
            name='f',
            field=models.FileField(blank=True, default='', upload_to=dm.models_shared.upload_to),
        ),
        migrations.AlterField(
            model_name='modelx',
            name='i',
            field=models.ImageField(blank=True, default='', upload_to=dm.models_shared.upload_to),
        ),
    ]
