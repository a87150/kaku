"""整页缓存的按需包装。

背景：Django 4.2 已进入 EOL，一批与 `cache_page()` 相关的缓存信息泄露漏洞
（如 CVE-2026-48588）只在 5.2+/6.0+ 修复；本项目因 django-notifications-hq
已停更、Meta 里用了 5.1 移除的 index_together 而暂时无法升级
（完整论证见 docs/django52-upgrade-assessment.md）。

而本项目恰好会踩到这个模式：文章/图画列表页用 `cache_page` 做整页缓存，
但页面顶栏与右侧抽屉里含当前登录用户的昵称、头像、未读通知数。
共享缓存一旦错误命中他人会话，就会把这些个人信息串给别的访客。

这里的处理不是关掉缓存，而是把整页缓存**只留给匿名访客**：
匿名渲染里不含任何私有数据，即使缓存键算错也无信息可泄露；
已登录请求直接进视图，渲染结果永不写入共享缓存。

配合 urls.py 中保留的 `vary_on_cookie`，两者是独立的两道防线。
"""
from functools import wraps

from django.views.decorators.cache import cache_page


def cache_page_anonymous(timeout, **kwargs):
    """与 cache_page 同参，但只对未登录请求做整页缓存。"""

    def decorator(view_func):
        cached_view = cache_page(timeout, **kwargs)(view_func)

        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = getattr(request, 'user', None)
            if user is not None and user.is_authenticated:
                return view_func(request, *args, **kwargs)
            return cached_view(request, *args, **kwargs)

        return _wrapped

    return decorator
