from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

import re

from actstream.signals import action
from notifications.signals import notify

from .models import Comment
from .forms import CommentCreationForm
from written.models import Article
from picture.models import Picture
from users.models import User


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreationForm
    template_name = 'comment/comment.html'

    def post(self, request, *args, **kwargs):
        try:
            latest_comment = request.user.comment_set.latest('created_time')
            if latest_comment.created_time + timezone.timedelta(seconds=60) > timezone.now():
                return HttpResponseForbidden('间隔小于 1 分钟，请稍微休息一会')
        except Comment.DoesNotExist:
            pass
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        return form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.referrer = self.request.META['HTTP_REFERER']
        self.ref = self.referrer.split('/')
        if self.ref[4] == 'article':
            self.obj = Article
        else:
            self.obj = Picture
        # Update the existing form kwargs dict with the request's user.
        kwargs.update({"user": self.request.user, "content_type": ContentType.objects.get_for_model(self.obj), "object_id": self.ref[5]})
        return kwargs
        
    def get_success_url(self):
        url = self.referrer
        comment = self.request.POST['content'] + ' '
        sender = self.request.user
        author = self.obj.objects.get(id=self.ref[5]).author
        target = self.obj.objects.get(id=self.ref[5])
        # 接受到评论会被 strip，不知道哪一步被处理的，临时为其补一个空格，防止@用户名在最后时无法解析

        nicknames = re.findall(r'@(?P<nickname>[a-zA-Z0-9\u0800-\u9fa5]+) ', comment)
        users = User.objects.filter(nickname__in=nicknames)
        comment = comment.strip()

        mentioned = False
        if users:
            def mark(mo):
                nickname = mo.group(1)
                user = users.get(nickname=nickname)
                return '@[%d](%s)' % (user.pk, user.get_absolute_url())

            pattern = '@(%s)' % ('|'.join(u.nickname for u in users))
            comment = re.sub(pattern, mark, comment)

            # 自己 @ 自己不会收到通知
            recipients = users.exclude(pk=sender.pk)

            if author in recipients:
                mentioned = True

            for recipient in recipients:
                data = {
                    'recipient': recipient,
                    'verb': '@你',
                    'target': target
                }
                notify.send(sender=sender, **data)

        # 如果帖子作者没被 @ 并且回复者不是作者自己，则向作者发送一条通知
        if not mentioned and sender != author:
            data = {
                'recipient': author,
                'verb': '评论了',
                'target': target
            }

            notify.send(sender=sender, **data)

        action.send(sender, verb='评论了', action_object=target)

        return url