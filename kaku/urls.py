"""Kaku 根 URL 配置。"""
from django.urls import path, re_path, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

import notifications.urls


urlpatterns = [
    re_path(r'', include('index.urls')),
    path('admin/', admin.site.urls),
    path('written/', include('written.urls')),
    path('picture/', include('picture.urls')),
    path('users/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('captcha/', include('captcha.urls')),
    path('comment/', include('comment.urls')),
    path('follow/', include('follow.urls')),
    path('oauth/', include('oauth.urls')),
    path('search/', include('search.urls')),
    re_path('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)