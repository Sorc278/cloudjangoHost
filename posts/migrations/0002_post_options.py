# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-19 13:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='options',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
    ]
