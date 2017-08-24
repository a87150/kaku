from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, UpdateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponse

from actstream.models import actor_stream, Action

from written.models import Article
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
        if len(request.FILES['mugshot']) >= 1024*1024:
            return HttpResponseForbidden("<h3>不能大于1mb</h3><a href=\"/users/mugshot/change/\">返回</a>")
        response = super().post(request, *args, **kwargs)
        return response

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
        articles = self.object.article_set.all().order_by('-created_time')[:10]
        actions = actor_stream(self.object)[:20]

        if self.object != self.request.user:
            actions = actions.exclude(verb__startswith='un')

        context.update({
            'article_list': articles,
            'action_list': actions,
        })
        return context


class UserActionView(ListView):
    paginate_by = 30
    model = Action
    template_name = 'users/actions.html'

    def get_queryset(self):
        return actor_stream(get_object_or_404(User, username=self.kwargs.get('username')))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=self.kwargs.get('username'))
        context['user'] = user
        return context


class UserArticleListView(ListView):
    paginate_by = 20
    model = Article
    template_name = 'users/articles.html'

    def get_queryset(self):
        return super().get_queryset().filter(author__username=self.kwargs.get('username')).order_by('-created_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=self.kwargs.get('username'))
        context['user'] = user
        return context