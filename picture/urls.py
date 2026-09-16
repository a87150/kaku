from django.urls import path, re_path
from django.views.decorators.vary import vary_on_cookie

from kaku.cache import cache_page_anonymous
from . import views

app_name = 'picture'

urlpatterns = [
    # 整页缓存只留给匿名访客：列表页顶栏/抽屉含登录用户信息，共享缓存有串号风险
    # （CVE-2026-48588，4.2 无补丁）。vary_on_cookie 作为第二道防线保留。
    path('', cache_page_anonymous(60 * 10)(vary_on_cookie(views.IndexView.as_view())), name='picture'),
    path('picture/<int:pk>/', views.Detail.as_view(), name='detail'),
    path('new/', views.PictureCreateView.as_view(), name='create'),
]