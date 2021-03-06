# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-27 16:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_post_options'),
        ('tags', '0005_auto_20170902_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagDeclination',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='posts.Post')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tags.Tag')),
            ],
        ),
        migrations.DeleteModel(
            name='TagSuggestion',
        ),
        migrations.AddIndex(
            model_name='tagdeclination',
            index=models.Index(fields=['post'], name='tags_tagdec_post_id_4c4b57_idx'),
        ),
    ]
