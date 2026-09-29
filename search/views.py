from django.views.generic import ListView

from index.models import Tag
from index.util import CONTENT_TYPES

# 每种类型最多返回多少条；再多时只提示“已截断”，不做分页
MAX_RESULTS_PER_TYPE = 20
VALID_TYPES = ('all',) + tuple(CONTENT_TYPES)


class SearchView(ListView):

    template_name = "search/search.html"
    context_object_name = "result_list"

    def get_queryset(self):
        # 关键词去掉首尾空格：用户在手机上很容易多打一个空格导致搜不到
        self.query = (self.request.GET.get('query') or '').strip()
        self.search_type = self.request.GET.get('type', 'all')
        if self.search_type not in VALID_TYPES:
            self.search_type = 'all'
        self.truncated = False
        self.result_count = 0

        if not self.query:
            return []

        tag = Tag.objects.filter(name=self.query).first()
        results = []
        # 各内容类型的搜索条件来自 CONTENT_TYPES，加类型不必改这里
        for key, meta in CONTENT_TYPES.items():
            if self.search_type not in ('all', key):
                continue
            queryset = meta['model'].objects.filter(
                meta['search_match'](self.query, tag)).distinct()
            if meta['defer']:
                queryset = queryset.defer(*meta['defer'])
            items, truncated = self._collect(queryset)
            for item in items:
                item.kaku_kind = meta['label']
                item.kaku_kind_key = key
            results.extend(items)
            self.truncated = self.truncated or truncated

        self.result_count = len(results)
        return results

    def _collect(self, queryset):
        """多取一条用来判断是否被截断，返回 (结果列表, 是否截断)。"""
        items = list(queryset[:MAX_RESULTS_PER_TYPE + 1])
        return items[:MAX_RESULTS_PER_TYPE], len(items) > MAX_RESULTS_PER_TYPE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query': self.query,
            'search_type': self.search_type,
            'truncated': self.truncated,
            'result_count': self.result_count,
        })
        return context
