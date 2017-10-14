from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone

from notifications.views import AllNotificationsList
from actstream.signals import action

from .models import Picture, Address
from .forms import PictureCreateForm
from index.pagination_data import pagination_data
from index.redis_caches import update_views, get_views, is_likes
from comment.forms import CommentCreationForm

class IndexView(ListView):

    paginate_by = 10
    model = Picture
    template_name = "picture/index.html"
    context_object_name = "picture_list"

    def get_queryset(self):
        return Picture.objects.prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_data = pagination_data(context.get('paginator'), 
                                    context.get('page_obj'),
                                    context.get('is_paginated'))

        context.update(page_data)

        return context


class Detail(DetailView):
    model = Picture
    template_name = "picture/detail.html"
    context_object_name = 'picture'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        update_views('picture', self.picture)
        return response

    def get_object(self, queryset=None):
        self.picture = super().get_object(queryset=None)
        return self.picture

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_list = self.object.tags.all()
        address_list = self.object.address_set.all()
        comment_list = self.object.comments.all()[:20]
        form = CommentCreationForm()
        views = get_views('picture', self.picture)

        if self.request.user.is_authenticated():
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
        if len(request.FILES['thematic']) >= 1024*1024:
            return HttpResponseForbidden("<h3>不能大于1mb</h3><a href=\"/picture/new/\">返回</a>")

        try:
            latest_picture = self.request.user.p_author.latest('created_time')
            if latest_picture.created_time + timezone.timedelta(seconds=60*6) > timezone.now():
                return HttpResponseForbidden('您的发图间隔小于 6 分钟，请稍微休息一会')
        except:
            pass

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