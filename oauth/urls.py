from django.urls import path
from . import views

app_name = 'oauth'
urlpatterns = [
    path('github/', views.GithubAuth.as_view(),name='github_oauth'),
    path('github_login/', views.githhub_login, name='github_login'),
]