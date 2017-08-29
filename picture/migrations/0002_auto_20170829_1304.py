# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-29 05:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('index', '0001_initial'),
        ('picture', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='picture',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
        migrations.AddField(
            model_name='picture',
            name='tags',
            field=models.ManyToManyField(blank=True, to='index.Tag', verbose_name='tags'),
        ),
        migrations.AddField(
            model_name='address',
            name='picture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='picture.Picture', verbose_name='picture'),
        ),
    ]
