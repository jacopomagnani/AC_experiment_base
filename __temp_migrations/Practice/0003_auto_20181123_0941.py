# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-23 05:41
from __future__ import unicode_literals

from django.db import migrations
import otree.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('Practice', '0002_auto_20181123_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='choice',
            field=otree.db.models.IntegerField(choices=[[1, 'Yes'], [0, 'No']], null=True),
        ),
    ]
