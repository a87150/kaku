import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, View

from actstream.models import Action, actor_stream
from actstream.signals import action

from .models import Follow
from users.models import User


class FollowView(LoginRequiredMixin, ListView):
    paginate_by = 20
    model = Action
    template_name = "follow/index.html"

    def get_queryset(self):
        follows = Follow.objects.filter(user=self.request.user)
        qs = Action.objects.none()

        for f in follows:
            a = actor_stream(f.follow_object).filter(
                timestamp__gt=timezone.now() - timezone.timedelta(days=10)
            )
            qs = qs | a
        return qs.order_by('-timestamp')


class FollowCreateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        object_id = request.POST.get('object_id')
        ftype = request.POST.get('ftype', '')

        if not object_id:
            return JsonResponse({'ok': False, 'msg': '缺少参数'})
        obj = get_object_or_404(User, id=object_id)

        if request.user == obj:
            return JsonResponse({'ok': False, 'msg': '不能关注自己'})

        if ftype == 'follow':
            try:
                f = Follow(user=request.user, follow_object=obj)
                f.save()
            except IntegrityError:
                return JsonResponse({'ok': False, 'msg': '早已关注'})
            action.send(request.user, verb='关注了', action_object=obj)
            return JsonResponse({'ok': True, 'msg': '成功'})

        elif ftype == 'unfollow':
            deleted, _ = Follow.objects.filter(user=request.user, follow_object=obj).delete()
            if not deleted:
                return JsonResponse({'ok': False, 'msg': '还未关注'})
            return JsonResponse({'ok': True, 'msg': '成功'})

        return JsonResponse({'ok': False, 'msg': '操作类型错误'})
