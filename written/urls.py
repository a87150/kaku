from django.conf.urls import url
from django.views.decorators.cache import cache_page

from . import views

app_name = 'written'
urlpatterns = [
    url(r'^$', cache_page(60 * 10)(views.IndexView.as_view()), name='index'),
    url(r'^article/(?P<pk>[0-9]+)/$', views.Detail.as_view(), name='detail'),
    url(r'^new/(?:(?P<slug>[\w-]+)/)?$', views.ArticleCreateView.as_view(), name='create'),
    url(r'^article/(?P<pk>[0-9]+)/edit/$', views.ArticleEditView.as_view(), name='edit'),
    url(r'^chapter/(?P<pk>[0-9]+)/$', views.ChapterDetail.as_view(), name='chapter'),
    url(r'^article/(?P<pk>[0-9]+)/new/$', views.ChapterCreateView.as_view(), name='create_chapter'),
]