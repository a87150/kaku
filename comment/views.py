from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from notifications.views import AllNotificationsList
from actstream.signals import action

from .models import Comment
from .forms import CommentCreationForm
from written.models import Article
from picture.models import Picture


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreationForm
    template_name = 'comment/comment.html'

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        return response

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.referrer = self.request.META['HTTP_REFERER']
        ref = self.referrer.split('/')
        if ref[4] == 'article':
            obj = Article
        else:
            obj = Picture
        # Update the existing form kwargs dict with the request's user.
        kwargs.update({"user": self.request.user, "content_type": ContentType.objects.get_for_model(obj), "object_id": ref[5]})
        return kwargs
        
    def get_success_url(self):
        url = self.referrer
        return url