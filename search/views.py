from django.db.models import Q
from django.views.generic import ListView

from written.models import Article
from picture.models import Picture
from index.models import Tag

# 每种类型最多返回多少条；再多时只提示“已截断”，不做分页
MAX_RESULTS_PER_TYPE = 20
VALID_TYPES = ('all', 'article', 'picture')


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

        if not self.query:
            self.result_count = 0
            return []

        tag = Tag.objects.filter(name=self.query).first()
        results = []

        if self.search_type in ('all', 'article'):
            items, truncated = self._collect(self._articles(tag))
            for item in items:
                item.kaku_kind = '文章'
                item.kaku_kind_key = 'article'
            results.extend(items)
            self.truncated = self.truncated or truncated

        if self.search_type in ('all', 'picture'):
            items, truncated = self._collect(self._pictures(tag))
            for item in items:
                item.kaku_kind = '图画'
                item.kaku_kind_key = 'picture'
            results.extend(items)
            self.truncated = self.truncated or truncated

        self.result_count = len(results)
        return results

    def _articles(self, tag):
        text_match = Q(title__icontains=self.query) | Q(content__icontains=self.query)
        if tag is not None:
            text_match |= Q(tags=tag)
        return Article.objects.filter(text_match).defer('content').distinct()

    def _pictures(self, tag):
        text_match = Q(title__icontains=self.query)
        if tag is not None:
            text_match |= Q(tags=tag)
        return Picture.objects.filter(text_match).distinct()

    def _collect(self, queryset):
        """多取一条用来判断是否被截断，返回 (结果列表, 是否截断)。"""
        items = list(queryset[:MAX_RESULTS_PER_TYPE + 1])
        return items[:MAX_RESULTS_PER_TYPE], len(items) > MAX_RESULTS_PER_TYPE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'query': getattr(self, 'query', ''),
            'search_type': getattr(self, 'search_type', 'all'),
            'truncated': getattr(self, 'truncated', False),
            'result_count': getattr(self, 'result_count', 0),
        })
        return context
