from django.urls import path, re_path
from django.views.decorators.vary import vary_on_cookie

from kaku.cache import cache_page_anonymous
from . import views

app_name = 'written'
urlpatterns = [
    # 整页缓存只留给匿名访客：列表页顶栏/抽屉含登录用户信息，共享缓存有串号风险
    # （CVE-2026-48588，4.2 无补丁）。vary_on_cookie 作为第二道防线保留。
    path('', cache_page_anonymous(60 * 10)(vary_on_cookie(views.IndexView.as_view())), name='index'),
    path('article/<int:pk>/', views.Detail.as_view(), name='detail'),
    re_path(r'^new/(?:(?P<slug>[\w-]+)/)?$', views.ArticleCreateView.as_view(), name='create'),
    path('article/<int:pk>/edit/', views.ArticleEditView.as_view(), name='edit'),
    path('chapter/<int:pk>/', views.ChapterDetail.as_view(), name='chapter'),
    path('article/<int:pk>/new/', views.ChapterCreateView.as_view(), name='create_chapter'),
]