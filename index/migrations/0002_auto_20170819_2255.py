# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-19 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('index', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
