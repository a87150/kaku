from django.conf.urls import url
from . import views

app_name = 'picture'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='picture'),
    url(r'^picture/(?P<pk>[0-9]+)/$', views.Detail.as_view(), name='detail'),
    url(r'^new/$', views.PictureCreateView.as_view(), name='create'),
    ]