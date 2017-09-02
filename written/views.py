from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone

import json

from notifications.views import AllNotificationsList
from actstream.signals import action
import mistune
import bleach

from .models import Article, Chapter
from .forms import ArticleCreationForm, ArticleEditForm, ChapterCreationForm
from index.pagination_data import pagination_data
from comment.forms import CommentCreationForm

class IndexView(ListView):

    paginate_by = 20
    model = Article
    template_name = "written/index.html"
    context_object_name = "article_list"

    def get_queryset(self):
        return Article.objects.defer('content').order_by("-created_time")
        
    def get_context_data(self, **kwargs):

        # 首先获得父类生成的传递给模板的字典。
        context = super().get_context_data(**kwargs)

        # 父类生成的字典中已有 paginator、page_obj、is_paginated 这三个模板变量，
        # paginator 是 Paginator 的一个实例，
        # page_obj 是 Page 的一个实例，
        # is_paginated 是一个布尔变量，用于指示是否已分页。
        # 例如如果规定每页 10 个数据，而本身只有 5 个数据，其实就用不着分页，此时 is_paginated=False。
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用自己写的 pagination_data 方法获得显示分页导航条需要的数据，见下方。
        page_data = pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模板变量更新到 context 中，注意 page_data 方法返回的也是一个字典。
        context.update(page_data)

        return context


def html_clean(htmlstr):
    markdown = mistune.Markdown()

    # 采用bleach来清除不必要的标签，并linkify text

    tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul', 'img']
    tags.extend(['p','hr','br','pre','code','span','h1','h2','h3','h4','h5','del','dl','img','sub','sup','u'
                 'table','thead','tr','th','td','tbody','dd','caption','blockquote','section'])
    attributes = {'*':['class','id'],'a': ['href', 'title','target'],'img':['src','style','width','height']}
    return bleach.linkify(bleach.clean(markdown(htmlstr),tags=tags,attributes=attributes))


class Detail(DetailView):
    model = Article
    template_name = "written/detail.html"

    context_object_name = 'article'

    def get(self, request, *args, **kwargs):
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 article 模型实例，即被访问的文章 article
        response = super().get(request, *args, **kwargs)

        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 article 的 content 值进行渲染
        article = super().get_object(queryset=None)
        if article:
            article.content = html_clean(article.content)
            return article

    def get_context_data(self, **kwargs):
        # 覆写 get_context_data 的目的是因为要把评论表单、article 下的评论列表传递给模板。
        context = super().get_context_data(**kwargs)
        tag_list = self.object.tags.all()
        chapter_list = self.object.chapter_set.all()[:20]
        comment_list = self.object.comments.all()[:20]
        form = CommentCreationForm()
        
        context.update({
            'tag_list': tag_list,
            'chapter_list': chapter_list,
            'comment_list': comment_list,
            'form': form,
        })
        return context


class ChapterDetail(DetailView):
    model = Chapter
    template_name = "written/chapter_detail.html"
    context_object_name = 'article'

    def get_object(self, queryset=None):
        article = super().get_object(queryset=None)

        if article:
            article.content = html_clean(article.content)
            return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_list = self.object.article.tags.all()

        context.update({
            'tag_list': tag_list,
        })
        return context
        
    def post(self, request, *args, **kwargs):
        id = request.POST['id']
        chap = get_object_or_404(Chapter, id=id)
        response_data = {}
        response_data['content'] = html_clean(chap.content)
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class ArticleCreateView(LoginRequiredMixin, CreateView):
    form_class = ArticleCreationForm
    template_name = 'written/post_written.html'

    def post(self, request, *args, **kwargs):
        # TODO：add rate limit
        try:
            latest_article = self.request.user.article_set.latest('created_time')
            if latest_article.created_time + timezone.timedelta(seconds=60) > timezone.now():
                return HttpResponseForbidden('您的发文间隔小于 1 分钟，请稍微休息一会')
        except Article.DoesNotExist:
            pass

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        action.send(self.request.user, verb='写了', action_object=self.object)
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Update the existing form kwargs dict with the request's user.
        kwargs.update({"user": self.request.user})
        return kwargs


class ArticleEditView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleEditForm
    template_name = 'written/post_written.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # TODO: use a more elegent way
        if self.request.user != self.object.author:
            return HttpResponseForbidden('只有作者才能编辑')
        return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if self.request.user != self.object.author:
            return HttpResponseForbidden('只有作者才能编辑')
        return response

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.helper.form_action = reverse('written:edit', kwargs={'pk': self.kwargs.get('pk')})
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        action.send(self.request.user, verb='编辑了', action_object=self.object)
        return response


class ChapterCreateView(LoginRequiredMixin, CreateView):
    model = Chapter
    form_class = ChapterCreationForm
    template_name = 'written/post_written.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)

        # TODO: use a more elegent way
        if self.request.user != Article.objects.get(id=self.kwargs.get('pk')).author:
            return HttpResponseForbidden('只有作者才能写子章节')
        return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if self.request.user != Article.objects.get(id=self.kwargs.get('pk')).author:
            return HttpResponseForbidden('只有作者才能写子章节')
        return response

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.helper.form_action = reverse('written:create_chapter', kwargs={'pk': self.kwargs.get('pk')})
        form.initial['article'] = [self.kwargs.get('pk')]
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        action.send(self.request.user, verb='写了新章节', action_object=self.object)
        return response

    
class NotificationsListView(AllNotificationsList):
    paginate_by = 10
    pass
        