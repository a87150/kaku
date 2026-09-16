"""分页链接工具。

原先模板里写死 `?page=N`，一旦列表页带上筛选参数（例如搜索的 query/type），
翻页就会把筛选条件丢掉。这里统一生成“保留当前查询串、只替换 page”的链接。
"""
from django import template
from django.http import QueryDict

register = template.Library()


@register.simple_tag(takes_context=True)
def page_url(context, page):
    request = context.get('request')
    params = request.GET.copy() if request is not None else QueryDict('', mutable=True)
    params['page'] = page
    return '?' + params.urlencode()
