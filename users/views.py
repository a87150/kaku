from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden

from actstream.models import actor_stream, Action

from written.models import Article
from picture.models import Picture
from follow.models import Follow
from .forms import UserProfileForm, MugshotForm
from .models import User


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'


class UserProfileChangeView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'users/profile_change.html'
    success_url = '/users/profile'

    def get_object(self, queryset=None):
        return self.request.user


class MugshotChangeView(LoginRequiredMixin, UpdateView):
    form_class = MugshotForm
    template_name = 'users/mugshot_change.html'
    success_url = '/users/profile'
    
    def post(self, request, *args, **kwargs):
        # 用 UploadedFile.size 判断大小；缺少文件时交给表单校验
        mugshot = request.FILES.get('mugshot')
        if mugshot is not None and mugshot.size >= 1024 * 1024:
            return HttpResponseForbidden(r'<h3>不能大于1mb</h3><a href="/users/mugshot/change/">返回</a>')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if form.has_changed():
            self.request.user.mugshot.delete(save=False)
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return User.objects.get(pk=self.request.user.pk)


class UserDetailView(DetailView):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'users/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        articles = self.object.a_author.all().defer('content')[:10]
        pictures = self.object.p_author.all()[:10]

        if self.request.user.is_authenticated:
            actions = actor_stream(self.object)[:20]
            # 当前登录用户是否已关注被查看的用户
            is_follow = Follow.objects.filter(
                user=self.request.user, follow_object=self.object
            ).exists()
        else:
            actions = {}
            is_follow = False

        context.update({
            'article_list': articles,
            'picture_list': pictures,
            'action_list': actions,
            'is_follow': is_follow,
        })
        return context


class UserActionView(ListView):
    paginate_by = 30
    model = Action
    template_name = 'users/actions.html'

    def get_queryset(self):
        return actor_stream(get_object_or_404(User, username=self.kwargs.get('username')))


class UserArticleListView(ListView):
    paginate_by = 20
    model = Article
    template_name = 'users/articles.html'

    def get_queryset(self):
        return super().get_queryset().filter(author__username=self.kwargs.get('username')).defer('content')


class UserPictureListView(ListView):
    paginate_by = 20
    model = Picture
    template_name = 'users/picture.html'

    def get_queryset(self):
        return super().get_queryset().filter(author__username=self.kwargs.get('username'))