# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-29 05:04
from __future__ import unicode_literals

from django.db import migrations, models
import picture.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(max_length=6000)),
            ],
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50, verbose_name='title')),
                ('thematic', models.ImageField(upload_to=picture.models.pictures_path, verbose_name='题图')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('views', models.PositiveIntegerField(default=0, editable=False, verbose_name='views')),
                ('likes', models.PositiveIntegerField(default=0, editable=False, verbose_name='likes')),
            ],
            options={
                'verbose_name': 'Picture',
                'verbose_name_plural': 'Pictures',
                'ordering': ['-created_time'],
            },
        ),
    ]
