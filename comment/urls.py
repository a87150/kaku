from django.conf.urls import url
from . import views

app_name = 'comment'
urlpatterns = [
    url(r'^$', views.CommentCreateView.as_view(), name='create'),
]