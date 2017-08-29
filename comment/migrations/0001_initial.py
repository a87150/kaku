# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-29 05:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True, max_length=300)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('likes', models.PositiveIntegerField(default=0, editable=False)),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['-created_time'],
            },
        ),
    ]
