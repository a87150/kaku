"""kaku URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

import notifications.urls


urlpatterns = [
    url(r'', include('index.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^written/', include('written.urls')),
    url(r'^picture/', include('picture.urls')),
    url(r'^users/', include('allauth.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^comment/', include('comment.urls')),
    url(r'^follow/', include('follow.urls')),
    url(r'^oauth/', include('oauth.urls')),
    url(r'^search/', include('search.urls')),
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)