from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from notifications.views import AllNotificationsList
from notifications.models import Notification
from actstream.signals import action

from .models import Tag
from .redis_caches import like, dislike
from .util import *


def index(request):
    return render(request, 'index.html', context={
                      'welcome': '欢迎访问kaku'})


def drawer(request):
    return render(request, 'drawer.html', context={})


class TagCreateView(LoginRequiredMixin, View):

    template_name = 'post_tag.html'

    def post(self, request, *args, **kwargs):
        pk = request.POST['pk']
        type = what_type(request.POST['type'])

        if type:
            obj = get_object_or_404(type, id=pk)
        else:
            return HttpResponseForbidden('类型错误')

        if obj.tags.count() >= 10:
            return HttpResponse("超过10个tag")
        else:
            try:
                t = Tag(name=request.POST['tag'])
                t.save()
            except:
                t = Tag.objects.get(name=request.POST['tag'])

            obj.tags.add(t)
            return HttpResponse("成功")


class LikeCreateView(LoginRequiredMixin, View):

    template_name = 'post_like.html'

    def post(self, request, *args, **kwargs):

        pk = request.POST['pk']
        user = request.user
        type = what_type(request.POST['type'])

        if type:
            obj = get_object_or_404(type, id=pk)
        else:
            return HttpResponseForbidden('类型错误')

        if request.POST['ltype']=='like':
            like(request.POST['type'], obj, user)
            action.send(sender=user, verb='赞了', action_object=obj)
            return HttpResponse("成功")
        else:
            dislike(request.POST['type'], obj, user)
            return HttpResponse("成功")


class NotificationsListView(AllNotificationsList):
    template_name = 'notifications/list.html'
    context_object_name = 'notice_list'
    paginate_by = 10

    def get_queryset(self):
        Notification.objects.mark_all_as_read(self.request.user)
        if getattr(settings, 'NOTIFICATIONS_SOFT_DELETE', False):
            qs = self.request.user.notifications.active()
        else:
            qs = self.request.user.notifications.all()
        return qs