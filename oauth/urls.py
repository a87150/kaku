from django.conf.urls import url
from . import views

app_name = 'oauth'
urlpatterns = [
    url(r'^github/$', views.GithubAuth.as_view(),name='github_oauth'),
    url(r'^github_login/$', views.githhub_login, name='github_login'),
]