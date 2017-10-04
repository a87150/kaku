# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-25 12:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('index', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50, verbose_name='title')),
                ('content', models.TextField(verbose_name='content')),
                ('excerpt', models.CharField(blank=True, max_length=100, null=True, verbose_name='excerpt')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('last_modified_time', models.DateTimeField(auto_now=True, verbose_name='last modified time')),
                ('views', models.PositiveIntegerField(default=0, editable=False, verbose_name='views')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='a_author', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, related_name='a_likes', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(blank=True, to='index.Tag', verbose_name='tags')),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='title')),
                ('content', models.TextField(verbose_name='content')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('last_modified_time', models.DateTimeField(auto_now=True, verbose_name='last modified time')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='written.Article', verbose_name='article')),
            ],
        ),
    ]