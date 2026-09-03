from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'picture'

urlpatterns = [
    path('', cache_page(60 * 10)(views.IndexView.as_view()), name='picture'),
    path('picture/<int:pk>/', views.Detail.as_view(), name='detail'),
    path('new/', views.PictureCreateView.as_view(), name='create'),
]