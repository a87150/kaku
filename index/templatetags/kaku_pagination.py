"""分页链接工具。

模板里曾经写死 ?page=N，一旦列表页带上筛选参数（例如搜索的 query/type），
翻页就会把筛选条件丢掉。page_url 统一生成“保留当前查询串、只替换 page”的链接。
页码窗口交给 Django 3.2+ 自带的 Paginator.get_elided_page_range。
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


@register.simple_tag
def elided_page_range(page_obj):
    """带省略号的页码列表，如 [1, '…', 4, 5, 6, '…', 10]。"""
    return page_obj.paginator.get_elided_page_range(page_obj.number)
