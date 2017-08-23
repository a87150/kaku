from django.conf.urls import url
from . import views

app_name = 'users'
urlpatterns = [
    url(r'^profile/$', views.UserProfileView.as_view(), name='profile'),
    url(r'^profile/change/$', views.UserProfileChangeView.as_view(), name='profile_change'),
    url(r'^mugshot/change/$', views.MugshotChangeView.as_view(), name='mugshot_change'),
    url(r'^(?P<username>[\w.@+-]+)/$', views.UserDetailView.as_view(), name='detail'),
    url(r'^(?P<username>[\w.@+-]+)/articles/$', views.UserArticleListView.as_view(), name='articles'),
    url(r'^(?P<username>[\w.@+-]+)/actions/$', views.UserActionView.as_view(), name='actions'),
]