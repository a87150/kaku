from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

app_name = 'index'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^drawer/.*$', views.drawer, name='drawer'),
    url(r'^tags/$', views.TagCreateView.as_view(), name='tags'),
    url(r'^like/$', views.LikeCreateView.as_view(), name='like'),
    url(r'^notifications/$', views.NotificationsListView.as_view(), name='notifications'),
    url(r'^accounts/profile/$', views.index, name='index')
]