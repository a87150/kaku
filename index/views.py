from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

import re

from notifications.views import AllNotificationsList
from notifications.models import Notification

from written.models import Article
from picture.models import Picture
from .models import Tag

def index(request):
    return render(request, 'index.html', context={
                      'welcome': '欢迎访问kaku'
                  })
                  
                  
class TagCreateView(LoginRequiredMixin, View):

    template_name = 'post_tag.html'

    def post(self, request, *args, **kwargs):

        id = request.POST['id']
        if request.POST['type'] == 'article':
            obj = get_object_or_404(Article, id=id)
        else:
            obj = get_object_or_404(Picture, id=id)
        try:
            if len(obj.tags.all()) >= 10:
                return HttpResponse("超过10个tag")
            else:
                t=Tag(name=request.POST['tag'])
                t.save()
                obj.tags.add(Tag.objects.get(id=t.id))
                return HttpResponse("成功")
        except:
            try:
                obj.tags.add(Tag.objects.get(name=request.POST['tag']))
                return HttpResponse("成功")
            except:
                return HttpResponse("失败")


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