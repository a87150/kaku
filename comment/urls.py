from django.urls import path
from . import views

app_name = 'comment'
urlpatterns = [
    # 被评论对象用 ContentType 主键 + 对象主键表达，任何模型都能评，无需注册
    path('create/<int:ct_id>/<int:pk>/', views.CommentCreateView.as_view(), name='create'),
]
