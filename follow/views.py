from django.views.generic import View, ListView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils import timezone

from notifications.views import AllNotificationsList
from actstream.signals import action
from actstream.models import Action, actor_stream

from .models import Follow
from users.models import User


class FollowView(LoginRequiredMixin, ListView):

    paginate_by = 20
    model = Action
    template_name = "follow/index.html"

    def get_queryset(self):
        follows = Follow.objects.filter(user=self.request.user)
        s = Action.objects.filter(actor_object_id='0')

        for f in follows:
            a = actor_stream(f.follow_object).filter(timestamp__gt = timezone.now() - timezone.timedelta(days=10))
            s = s | a
        return s.order_by('-timestamp')
        

class FollowCreateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        object = get_object_or_404(User, id=request.POST['object_id'])

        if request.POST['ftype'] == 'follow':
            try:
                if request.user == object:
                    return HttpResponse('不能关注自己')
                else:
                    f = Follow(user=request.user, follow_object=object)
                    f.save()
                    action.send(request.user, verb='关注了', action_object=object)
                    return HttpResponse('成功')
            except:
                return HttpResponse('早已关注')

        else:
            try:
                get_object_or_404(Follow, user=request.user, follow_object=object).delete()
                return HttpResponse('成功')
            except:
                return HttpResponse('失败')