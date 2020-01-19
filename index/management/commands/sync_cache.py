from django.core.management.base import BaseCommand, CommandError
from django.db import models

import os

from index.redis_caches import sync_views, sync_like

class Command(BaseCommand):

     def handle(self, *args, **options):
         sync_views('article')
         sync_views('picture')
         sync_like('article')
         sync_like('picture')
         print('over!')