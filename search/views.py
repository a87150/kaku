from django.views.generic import ListView
from django.db.models import Q

from itertools import chain

from written.models import Article
from picture.models import Picture
from index.models import Tag


class SearchView(ListView):

    template_name = "search/search.html"
    context_object_name = "result_list"

    def get_queryset(self):
        q = self.request.GET.get('query', '')

        if not q:
            return []

        search_type = self.request.GET.get('type', 'all')

        def _search_articles():
            try:
                t = Tag.objects.get(name=q)
                return (Article.objects
                        .filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(tags=t))
                        .defer('content').distinct())
            except Tag.DoesNotExist:
                return (Article.objects
                        .filter(Q(title__icontains=q) | Q(content__icontains=q))
                        .defer('content').distinct())

        def _search_pictures():
            try:
                t = Tag.objects.get(name=q)
                return (Picture.objects
                        .filter(Q(title__icontains=q) | Q(tags=t)).distinct())
            except Tag.DoesNotExist:
                return Picture.objects.filter(title__icontains=q).distinct()

        if search_type == 'article':
            return list(_search_articles()[:20])

        elif search_type == 'picture':
            return list(_search_pictures()[:20])

        else:  # all
            return list(chain(_search_articles()[:20], _search_pictures()[:20]))
