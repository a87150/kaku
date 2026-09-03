from django.urls import path, re_path
from . import views

app_name = 'users'
urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/change/', views.UserProfileChangeView.as_view(), name='profile_change'),
    path('mugshot/change/', views.MugshotChangeView.as_view(), name='mugshot_change'),
    re_path(r'^(?P<username>[\w.@+-]+)/$', views.UserDetailView.as_view(), name='detail'),
    re_path(r'^(?P<username>[\w.@+-]+)/articles/$', views.UserArticleListView.as_view(), name='articles'),
    re_path(r'^(?P<username>[\w.@+-]+)/actions/$', views.UserActionView.as_view(), name='actions'),
    re_path(r'^(?P<username>[\w.@+-]+)/pictures/$', views.UserPictureListView.as_view(), name='pictures'),
]