from django.urls import path

from . import views

app_name = 'index'
urlpatterns = [
    path('', views.index, name='index'),
    path('tags/', views.TagCreateView.as_view(), name='tags'),
    path('like/', views.LikeCreateView.as_view(), name='like'),
    path('notifications/', views.NotificationsListView.as_view(), name='notifications'),
    path('accounts/profile/', views.index, name='index')
]