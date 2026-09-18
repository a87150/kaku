"""Django settings for kaku project.

文档：
  https://docs.djangoproject.com/en/5.2/topics/settings/
  https://docs.djangoproject.com/en/5.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_dotenv(path=None):
    """极简 .env 读取：把 KEY=VALUE 写入环境变量（不覆盖已有值）。"""
    env_file = path or os.path.join(BASE_DIR, '.env')
    if not os.path.exists(env_file):
        return
    with open(env_file, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ.setdefault(key, value)


def _env_bool(name, default=False):
    """读取布尔型环境变量：1/true/yes/on（忽略大小写与首尾空格）视为真。"""
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ('1', 'true', 'yes', 'on')


def _env_list(name):
    """读取逗号分隔的环境变量，丢弃空白项。"""
    raw = os.environ.get(name, '')
    return [item.strip() for item in raw.split(',') if item.strip()]


_load_dotenv()


# SECURITY WARNING: keep the secret key used in production secret!
# 默认值仅用于本地开发；生产/上线请通过环境变量 DJANGO_SECRET_KEY 注入
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'dev-only-do-not-use-in-production-key-4f8a2c9e1b7d6f5a3c0e2b8d9f1a4c7e'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _env_bool('DJANGO_DEBUG', True)

ALLOWED_HOSTS = _env_list('DJANGO_ALLOWED_HOSTS') or [
    'takanashi.site', '127.0.0.1', 'localhost', '192.168.1.104']
SITE_ID = 1

# 反向代理/HTTPS 域名需要显式列入，否则 Django 会拒绝跨源 POST（含登录、CSRF）
# 例：DJANGO_CSRF_TRUSTED_ORIGINS=https://takanashi.site,https://www.takanashi.site
CSRF_TRUSTED_ORIGINS = _env_list('DJANGO_CSRF_TRUSTED_ORIGINS')

# ===== 生产 HTTPS 相关安全项：默认全部关闭，按需用 DJANGO_HTTPS=1 打开 =====
# 之所以不跟随 DEBUG 自动开启：若 nginx 只监听 80 端口，SECURE_SSL_REDIRECT
# 会造成 http -> https -> 无人监听 的重定向环，把站点彻底打不开。
if _env_bool('DJANGO_HTTPS'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# 这两项与 Django 默认值一致，写出仅为让上线检查清单可逐条核对
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'crispy_forms',
    # crispy-forms 2.x 起模板包拆分为独立发行包；本项目表单页用 Bootstrap 5
    'crispy_bootstrap5',
    'captcha',
    'actstream',
    'notifications',
    'imagekit',
    
    'users',
    'picture',
    'written',
    'index',
    'comment',
    'follow',
    'oauth',
    'search',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'kaku.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'kaku.context_processors.recent_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'kaku.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# 保持旧项目使用 AutoField 作为隐式主键，避免引入迁移
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


# cache
# 说明：未运行 Redis 时自动降级（IGNORE_EXCEPTIONS + 关闭重试退避），页面不会因 Redis 不可用而变慢或报错

from redis.retry import Retry
from redis.backoff import NoBackoff

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "KEY_PREFIX": "example",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry": Retry(NoBackoff(), 1),
                "socket_connect_timeout": 0.3,
            },
            "IGNORE_EXCEPTIONS": True,
        }
    }
}

# File storage
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Internationalization
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'common_static'),
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# account

LOGIN_URL = "/users/login/"

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_ADAPTER = 'users.adapter.AccountAdapter'
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['username*', 'email*', 'password1*', 'password2*']
ACCOUNT_FORMS = {
    'login': 'users.forms.LoginForm',
    'signup': 'users.forms.SignupForm',
}
ACCOUNT_USERNAME_MIN_LENGTH = 3
# 这里必须是指向 list 的路径（list 里放可调用的校验器），写成别的形式注册会 500
ACCOUNT_USERNAME_VALIDATORS = 'users.validators.username_validators'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
# 2.x 起必须显式声明允许的模板包，否则 {% crispy %} 找不到 bootstrap5
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# github oauth —— 通过环境变量注入，避免把密钥写进代码仓库
# 本地可新建 .env（参照 .env.example）或在 shell 设置环境变量：
#   GITHUB_CLIENTID / GITHUB_CLIENTSECRET / GITHUB_CALLBACK / DJANGO_SECRET_KEY

GITHUB_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
GITHUB_CLIENTID = os.environ.get('GITHUB_CLIENTID', '')
GITHUB_CLIENTSECRET = os.environ.get('GITHUB_CLIENTSECRET', '')

# 这里是github认证处理的url,就是自己处理登陆逻辑
GITHUB_CALLBACK = os.environ.get('GITHUB_CALLBACK', 'http://127.0.0.1:8000/oauth/github/')

'''
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
        },
    },
}

'''