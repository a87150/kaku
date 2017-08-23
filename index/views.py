from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

import re

from written.models import Article
from picture.models import Picture
from .models import Tag

def index(request):
    return render(request, 'index.html', context={
                      'welcome': '欢迎访问kaku'
                  })
                  
                  
class TagCreateView(LoginRequiredMixin, View):

    template_name = 'post_tag.html'

    def post(self, request, *args, **kwargs):

        id = request.POST['id']
        if request.POST['type'] == 'article':
            obj = Article.objects.get(id=id)
        else:
            obj = Picture.objects.get(id=id)
        try:
            if len(obj.tags.all()) >= 10:
                return HttpResponse("超过10个tag")
            else:
                t=Tag(name=request.POST['tag'])
                t.save()
                obj.tags.add(Tag.objects.get(id=t.id))
                return HttpResponse("成功")
        except:
            try:
                obj.tags.add(Tag.objects.get(name=request.POST['tag']))
                return HttpResponse("成功")
            except:
                return HttpResponse("失败")