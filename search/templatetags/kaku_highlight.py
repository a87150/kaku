"""搜索结果关键词高亮。

实现要点：先用 re.split 按关键词切开原文，再对**每一段单独**做 HTML 转义，
最后把命中的片段包进 <mark>。这样不会出现“先整体转义、再在 &amp; 这种实体
中间插入标签”导致的非法标记。
"""
import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def highlight(text, query):
    """把 text 中命中 query 的片段包成 <mark>，其余内容照常转义。"""
    text = '' if text is None else str(text)
    query = (query or '').strip()
    if not query:
        return escape(text)

    parts = re.split('(%s)' % re.escape(query), text, flags=re.IGNORECASE)
    out = []
    for index, part in enumerate(parts):
        if not part:
            continue
        if index % 2:
            out.append('<mark class="kaku-mark">%s</mark>' % escape(part))
        else:
            out.append(escape(part))
    return mark_safe(''.join(out))
