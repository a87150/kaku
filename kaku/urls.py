"""kaku URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import path, include
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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