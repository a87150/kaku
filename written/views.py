from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils import timezone

import re

from actstream.signals import action
import mistune
import bleach

from .models import Article, Chapter
from .forms import ArticleCreationForm, ArticleEditForm, ChapterCreationForm
from index.util import is_likes, update_views
from comment.forms import CommentCreationForm


class IndexView(ListView):

    paginate_by = 10
    model = Article
    template_name = "written/index.html"
    context_object_name = "article_list"

    def get_queryset(self):
        # 列表卡片要显示点赞/评论数：一次 annotate 聚合，避免每张卡片多查两次。
        # 注意：annotate 走 GROUP BY，Django 会忽略 Meta.ordering，所以必须显式
        # order_by，否则分页顺序不确定（UnorderedObjectListWarning / 翻页串数据）。
        return (Article.objects
                .defer('content')
                .select_related('author')
                .prefetch_related('tags')
                .annotate(like_count=Count('likes', distinct=True),
                          comment_count=Count('comments', distinct=True))
                .order_by('-created_time'))

# 编辑器工具栏（EasyMDE）会产出 GFM 语法，这里启用对应 mistune 插件：
#   table —— 管道表格；strikethrough —— ~~删除线~~
MARKDOWN_PLUGINS = ['table', 'strikethrough']

# mistune 表格插件输出 style="text-align:x"，bleach 白名单不保留 style，
# 这里转成等价的 align 属性（安全属性，无脚本风险），保留表格对齐效果
_TABLE_ALIGN_RE = re.compile(
    r'(<(?:th|td)\b[^>]*?)\s+style="text-align:(left|center|right)"')


def html_clean(htmlstr):
    markdown = mistune.create_markdown(escape=False, plugins=MARKDOWN_PLUGINS)

    # 采用bleach来清除不必要的标签，并linkify text
    tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
            'strong', 'ul', 'img', 'table', 'p', 'hr', 'br', 'pre', 'span', 'h1', 'h2',
            'h3', 'h4', 'h5', 'del', 'dl', 'sub', 'sup', 'u', 'thead', 'tr', 'th', 'td',
            'tbody', 'dd', 'caption', 'section']
    # 不放行 a[target]：正文里的 target="_blank" 会带来反向 tabnabbing
    attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'width', 'height'],
        'th': ['align'],
        'td': ['align'],
    }
    rendered = _TABLE_ALIGN_RE.sub(r'\1 align="\2"', markdown(htmlstr))
    return bleach.linkify(bleach.clean(rendered, tags=tags, attributes=attributes))


class Detail(DetailView):
    model = Article
    template_name = "written/detail.html"
    context_object_name = 'article'

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 article 的 content 值进行渲染。
        # 浏览计数也必须在这里自增：放到 super().get() 之后会先渲染再计数，
        # 页面上的「浏览」永远比真实值少 1。
        self.article = super().get_object(queryset=None)
        self.article.content = html_clean(self.article.content)
        update_views('article', self.article)
        return self.article

    def get_context_data(self, **kwargs):
        # 覆写 get_context_data 的目的是因为要把评论表单、article 下的评论列表传递给模板。
        context = super().get_context_data(**kwargs)
        tag_list = self.object.tags.all()
        chapter_list = self.object.chapter_set.all()[:20]
        comment_list = self.object.comments.all()[:20]
        form = CommentCreationForm(target=self.object)
        views = self.article.views

        if self.request.user.is_authenticated:
            is_like = is_likes('article', self.article, self.request.user)
        else:
            is_like = False

        context.update({
            'tag_list': tag_list,
            'chapter_list': chapter_list,
            'comment_list': comment_list,
            'form': form,
            'views': views,
            'is_like': is_like,
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
        pk = request.POST.get('pk')
        if not pk:
            return JsonResponse({'ok': False, 'msg': '缺少参数'}, status=400)
        chap = get_object_or_404(Chapter, pk=pk)
        return JsonResponse({'content': html_clean(chap.content)})


class ArticleCreateView(LoginRequiredMixin, CreateView):
    form_class = ArticleCreationForm
    template_name = 'written/post_written.html'

    def post(self, request, *args, **kwargs):
        try:
            latest_article = self.request.user.a_author.latest('created_time')
        except ObjectDoesNotExist:
            latest_article = None
        if (latest_article is not None
                and latest_article.created_time + timezone.timedelta(seconds=60*3) > timezone.now()):
            return HttpResponseForbidden('您的发文间隔小于 3 分钟，请稍微休息一会')

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        action.send(sender=self.request.user, verb='写了', action_object=self.object)
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

    def get_object(self, queryset=None):
        # 鉴权必须发生在对象加载处。原来的 get()/post() 覆写都在 super() 之后才检查，
        # 而 POST 时父类已经 form.save() 落库 —— 非作者能把别人的文章改完才拿到 403。
        # 这里统一提前 404，且不泄露文章是否存在。
        article = super().get_object(queryset=queryset)
        if article.author_id != self.request.user.pk:
            raise Http404
        return article

    def form_valid(self, form):
        response = super().form_valid(form)
        action.send(sender=self.request.user, verb='编辑了', action_object=self.object)
        return response


class ChapterCreateView(LoginRequiredMixin, CreateView):
    model = Chapter
    form_class = ChapterCreationForm
    template_name = 'written/post_written.html'

    def get_parent_article(self):
        """父文章只从 URL 取并当场鉴权：放进表单字段等于让用户自选父文章。"""
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        if article.author_id != self.request.user.pk:
            raise Http404
        return article

    def get_form_kwargs(self):
        # GET 与 POST 都会经过这里，鉴权因此先于任何写入
        kwargs = super().get_form_kwargs()
        kwargs['article'] = self.get_parent_article()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chapter_article_pk'] = self.kwargs.get('pk')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        action.send(sender=self.request.user, verb='写了新章节', action_object=self.object)
        return response
