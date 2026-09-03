from django.urls import path
from . import views

app_name = 'follow'
urlpatterns = [
    path('', views.FollowView.as_view(), name='follow'),
    path('create/', views.FollowCreateView.as_view(), name='create'),
]