from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'written'
urlpatterns = [
    path('', cache_page(60 * 10)(views.IndexView.as_view()), name='index'),
    path('article/<int:pk>/', views.Detail.as_view(), name='detail'),
    re_path(r'^new/(?:(?P<slug>[\w-]+)/)?$', views.ArticleCreateView.as_view(), name='create'),
    path('article/<int:pk>/edit/', views.ArticleEditView.as_view(), name='edit'),
    path('chapter/<int:pk>/', views.ChapterDetail.as_view(), name='chapter'),
    path('article/<int:pk>/new/', views.ChapterCreateView.as_view(), name='create_chapter'),
]