from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

app_name = 'picture'

urlpatterns = [
    url(r'^$', cache_page(60 * 10)(views.IndexView.as_view()), name='picture'),
    url(r'^picture/(?P<pk>[0-9]+)/$', cache_page(60 * 1)(views.Detail.as_view()), name='detail'),
    url(r'^new/$', views.PictureCreateView.as_view(), name='create'),
    ]