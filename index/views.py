from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from notifications.models import Notification
from notifications.views import AllNotificationsList
from actstream.signals import action

from .models import Tag
from .redis_caches import like, dislike
from .util import what_type


def index(request):
    return render(request, 'index.html', context={'welcome': '欢迎访问kaku'})


class TagCreateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        obj_type = what_type(request.POST.get('type'))

        if not obj_type or not pk:
            return JsonResponse({'ok': False, 'msg': '类型错误'})

        obj = get_object_or_404(obj_type, id=pk)

        if obj.tags.count() >= 10:
            return JsonResponse({'ok': False, 'msg': '超过10个tag'})

        tag_name = request.POST.get('tag', '')
        if not tag_name:
            return JsonResponse({'ok': False, 'msg': '标签不能为空'})

        t, _ = Tag.objects.get_or_create(name=tag_name)
        if obj.tags.filter(pk=t.pk).exists():
            return JsonResponse({'ok': False, 'msg': '已添加过该标签'})

        obj.tags.add(t)
        return JsonResponse({'ok': True, 'msg': '成功'})


class LikeCreateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        user = request.user
        obj_type = what_type(request.POST.get('type'))

        if not obj_type or not pk:
            return JsonResponse({'ok': False, 'msg': '类型错误'})

        obj = get_object_or_404(obj_type, id=pk)

        if request.POST.get('ltype') == 'like':
            like(request.POST['type'], obj, user)
            action.send(sender=user, verb='赞了', action_object=obj)
            return JsonResponse({'ok': True, 'msg': '成功'})
        else:
            dislike(request.POST['type'], obj, user)
            return JsonResponse({'ok': True, 'msg': '成功'})


class NotificationsListView(AllNotificationsList):
    template_name = 'notifications/list.html'
    context_object_name = 'notice_list'
    paginate_by = 10

    def get_queryset(self):
        # 不再在打开列表时全部标记已读（保持未读徽标，由用户点击单条时标记）
        qs = self.request.user.notifications.all()
        return qs.select_related('actor_content_type', 'target_content_type')
