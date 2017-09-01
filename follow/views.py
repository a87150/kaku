from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from notifications.views import AllNotificationsList
from actstream.signals import action

from .models import Follow
from users.models import User

class FollowCreateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, nickname=request.user)
        object_id = get_object_or_404(User, id=request.POST['object_id'])
        if request.POST['ftype'] == 'follow':
            try:
                if user==object_id:
                    return HttpResponse('不能关注自己')
                else:
                    f = Follow(user=user, follow_object=object_id)
                    f.save()
                    return HttpResponse('成功')
            except IntegrityError:
                return HttpResponse('早已关注')
                
        else:
            try:
                get_object_or_404(Follow, user=user, follow_object=object_id).delete()
                return HttpResponse('成功')
            except:
                return HttpResponse('失败')