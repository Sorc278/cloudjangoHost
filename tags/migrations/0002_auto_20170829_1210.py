# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-29 12:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='tagsuggestion',
            index=models.Index(fields=['post', 'tag'], name='tags_tagsug_post_id_106df2_idx'),
        ),
        migrations.AddIndex(
            model_name='tagchance',
            index=models.Index(fields=['child'], name='tags_tagcha_child_i_f15b7d_idx'),
        ),
    ]
