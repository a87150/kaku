"""内容类型注册表，以及浏览量与点赞的读写。

浏览量和点赞数的唯一事实源是数据库。历史上它们先写 Redis、再由
manage.py sync_cache 手工落库，于是列表页读库、详情页读 Redis 成了两套真相
（赞数永远不涨、Redis 重启即丢），测试也被迫连真实 Redis。现在全部直连数据库。
"""
from django.db.models import F, Q

from written.models import Article
from picture.models import Picture


def _article_match(query, tag):
    match = Q(title__icontains=query) | Q(content__icontains=query)
    return match | Q(tags=tag) if tag is not None else match


def _picture_match(query, tag):
    match = Q(title__icontains=query)
    return match | Q(tags=tag) if tag is not None else match


# 内容类型注册表：加一种内容类型 = 这里加一行（外加新 app 的模型）。
# label 用于搜索结果归类，search_match 返回该类型的搜索 Q 对象，
# defer 是列表/搜索时不必取回的重字段。
CONTENT_TYPES = {
    'article': {
        'model': Article,
        'label': '文章',
        'search_match': _article_match,
        'defer': ('content',),
    },
    'picture': {
        'model': Picture,
        'label': '图画',
        'search_match': _picture_match,
        'defer': (),
    },
}


def what_type(type):
    """把前端传入的类型名解析成模型类；不识别/为空返回 None。

    注意：参数名沿用历史命名 type，实际是类型字符串而非 Python 类型。
    """
    meta = CONTENT_TYPES.get(type) if type else None
    return meta['model'] if meta else None


def update_views(type, obj):
    """浏览量 +1 并立即落库（F 表达式，避免读改写竞态）。"""
    obj.__class__.objects.filter(pk=obj.pk).update(views=F('views') + 1)
    obj.views += 1


def like(type, obj, user):
    # ManyToMany.add 自带去重，重复点赞是幂等的
    obj.likes.add(user)


def dislike(type, obj, user):
    obj.likes.remove(user)


def is_likes(type, obj, user):
    return obj.likes.filter(pk=user.pk).exists()
