from django.conf.urls import url
from . import views

app_name = 'follow'
urlpatterns = [
    url(r'^create/$', views.FollowCreateView.as_view(), name='create'),
]