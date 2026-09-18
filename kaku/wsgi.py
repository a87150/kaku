"""WSGI 入口：生产环境由 gunicorn 以 kaku.wsgi:application 启动。"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kaku.settings")

application = get_wsgi_application()
