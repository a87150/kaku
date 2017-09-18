from django.core.management.base import BaseCommand, CommandError
from django.db import models

import os

from index.redis_caches import *

class Command(BaseCommand):
     def handle(self, *args, **options):
         sync_views('article')
         sync_views('picture')
         print('over!')