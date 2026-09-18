"""整页缓存的按需包装。

文章/图画列表页用 `cache_page` 做整页缓存，但这两个页面的顶栏与右侧抽屉里
含当前登录用户的昵称、头像、未读通知数。这类页面一旦进入共享缓存，
缓存键算错就会把个人信息串给别的访客。

所以整页缓存**只留给匿名访客**：
  - 匿名渲染里不含任何私有数据，即使缓存键算错也无信息可泄露；
  - 已登录请求直接进视图，渲染结果永不写入共享缓存。

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
