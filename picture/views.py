from django.views.generic import ListView, DetailView, CreateView
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.utils import timezone

from actstream.signals import action

from .models import Picture
from .forms import PictureCreateForm
from index.util import is_likes, update_views
from comment.forms import CommentCreationForm

class IndexView(ListView):

    paginate_by = 10
    model = Picture
    template_name = "picture/index.html"
    context_object_name = "picture_list"

    def get_queryset(self):
        # 列表卡片要显示点赞/评论数：一次 annotate 聚合，避免每张卡片多查两次。
        # 注意：annotate 走 GROUP BY，Django 会忽略 Meta.ordering，所以必须显式
        # order_by，否则分页顺序不确定（UnorderedObjectListWarning / 翻页串数据）。
        return (Picture.objects
                .select_related('author')
                .prefetch_related('tags')
                .annotate(like_count=Count('likes', distinct=True),
                          comment_count=Count('comments', distinct=True))
                .order_by('-created_time'))

class Detail(DetailView):
    model = Picture
    template_name = "picture/detail.html"
    context_object_name = 'picture'

    def get_object(self, queryset=None):
        self.picture = super().get_object(queryset=None)
        # 先计数再渲染，否则页面上的「浏览」永远比真实值少 1
        update_views('picture', self.picture)
        return self.picture

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_list = self.object.tags.all()
        address_list = self.object.address_set.all()
        comment_list = self.object.comments.all()[:20]
        form = CommentCreationForm(target=self.object)
        views = self.picture.views

        if self.request.user.is_authenticated:
            is_like = is_likes('picture', self.picture, self.request.user)
        else:
            is_like = False

        context.update({
            'tag_list': tag_list,
            'comment_list': comment_list,
            'form': form,
            'views': views,
            'is_like': is_like
        })
        return context


class PictureCreateView(LoginRequiredMixin, CreateView):
    form_class = PictureCreateForm
    template_name = 'picture/post_picture.html'

    def post(self, request, *args, **kwargs):
        # 与 users.MugshotChangeView 一致：用 UploadedFile.size，不去依赖 len()
        thematic = request.FILES.get('thematic')
        if thematic is not None and thematic.size >= 1024 * 1024:
            return HttpResponseForbidden("<h3>不能大于1mb</h3><a href=\"/picture/new/\">返回</a>")

        try:
            latest_picture = self.request.user.p_author.latest('created_time')
        except ObjectDoesNotExist:
            latest_picture = None
        if (latest_picture is not None
                and latest_picture.created_time + timezone.timedelta(seconds=60*6) > timezone.now()):
            return HttpResponseForbidden('您的发图间隔小于 6 分钟，请稍微休息一会')

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        action.send(sender=self.request.user, verb='画了', action_object=self.object)
        return response

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Update the existing form kwargs dict with the request's user.
        kwargs.update({"user": self.request.user})
        return kwargs