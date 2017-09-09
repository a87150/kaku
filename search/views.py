from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.views.generic import ListView
from django.db.models import Q

from itertools import chain

from written.models import Article
from picture.models import Picture
from users.models import User
from index.models import Tag


class SearchView(ListView):

    template_name = "search/search.html"
    context_object_name = "search_list"

    def get_queryset(self):
        q = self.request.GET['query']
        
        if not q:
            return HttpResponseNotFound

        if 'type' in self.request.GET:
            type = self.request.GET['type']

            if type=='article':
                try:
                    t = Tag.objects.get(name=q)
                    a_list = Article.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).defer('content') | Article.objects.filter(tags=t).defer('content')
                except:
                    a_list = Article.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).defer('content')
                return a_list[:20]

            elif type=='picture':
                try:
                    t = Tag.objects.get(name=q)
                    p_list = Picture.objects.filter(title__icontains=q) | Picture.objects.filter(tags=t)
                except:
                    p_list = Picture.objects.filter(title__icontains=q)
                return p_list[:20]

        else:
            try:
                t = Tag.objects.get(name=q)
                a_list = Article.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).defer('content') | Article.objects.filter(tags=t).defer('content')
                p_list = Picture.objects.filter(title__icontains=q) | Picture.objects.filter(tags=t)
            except:
                a_list = Article.objects.filter(Q(title__icontains=q) | Q(content__icontains=q)).defer('content')
                p_list = Picture.objects.filter(title__icontains=q)
            return chain(a_list[:20], p_list[:20])
