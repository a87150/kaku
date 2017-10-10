from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from notifications.views import AllNotificationsList
from notifications.models import Notification

from written.models import Article
from picture.models import Picture
from .models import Tag
from .redis_caches import like, dislike

def index(request):
    return render(request, 'index.html', context={
                      'welcome': '欢迎访问kaku'})


def drawer(request):
    return render(request, 'drawer.html', context={})


class TagCreateView(LoginRequiredMixin, View):

    template_name = 'post_tag.html'

    def post(self, request, *args, **kwargs):
        pk = request.POST['pk']

        if request.POST['type'] == 'article':
            obj = get_object_or_404(Article, id=pk)
        else:
            obj = get_object_or_404(Picture, id=pk)

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
        type = request.POST['type']
        user = request.user

        if request.POST['type'] == 'article':
            obj = get_object_or_404(Article, id=pk)
        else:
            obj = get_object_or_404(Picture, id=pk)

        if request.POST['ltype']=='like':
            like(type, obj, user)
            return HttpResponse("成功")
        else:
            dislike(type, obj, user)
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