from django.conf.urls import url
from . import views

app_name = 'index'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tags/$', views.TagCreateView.as_view(), name='tags'),
    url(r'^notifications/$', views.NotificationsListView.as_view(), name='all'),
    url(r'^accounts/profile/$', views.index, name='index')
]