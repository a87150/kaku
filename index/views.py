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

from kaku.tagfields import MAX_TAGS_PER_ITEM, TAG_NAME_MAX_LEN


def index(request):
    return render(request, 'index.html', context={'welcome': '欢迎访问kaku'})


class TagCreateView(LoginRequiredMixin, View):
    """详情页给文章/图画即时添加标签，返回 JSON 由前端就地插入，不整页刷新。"""

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        obj_type = what_type(request.POST.get('type'))

        if not obj_type or not pk:
            return JsonResponse({'ok': False, 'msg': '类型错误'})

        obj = get_object_or_404(obj_type, id=pk)

        tag_name = (request.POST.get('tag') or '').strip()
        if not tag_name:
            return JsonResponse({'ok': False, 'msg': '标签不能为空'})

        if len(tag_name) > TAG_NAME_MAX_LEN:
            return JsonResponse({
                'ok': False,
                'msg': '标签太长（最多 %d 字）' % TAG_NAME_MAX_LEN,
            })

        if obj.tags.filter(name=tag_name).exists():
            return JsonResponse({'ok': False, 'msg': '已添加过该标签'})

        if obj.tags.count() >= MAX_TAGS_PER_ITEM:
            return JsonResponse({'ok': False, 'msg': '超过10个tag'})

        t, _ = Tag.objects.get_or_create(name=tag_name)
        obj.tags.add(t)
        # 回传服务端最终采用的标签名，前端据此生成标签块
        return JsonResponse({'ok': True, 'msg': '成功', 'tag': t.name})


class TagDeleteView(LoginRequiredMixin, View):
    """从文章/图画上摘掉一个标签。

    与添加不同，移除只允许作者本人操作——否则任何登录用户都能改别人的标签。
    """

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk')
        obj_type = what_type(request.POST.get('type'))

        if not obj_type or not pk:
            return JsonResponse({'ok': False, 'msg': '类型错误'})

        obj = get_object_or_404(obj_type, id=pk)

        if getattr(obj, 'author_id', None) != request.user.id:
            return JsonResponse({'ok': False, 'msg': '只有作者可以移除标签'}, status=403)

        tag_name = (request.POST.get('tag') or '').strip()
        if not tag_name:
            return JsonResponse({'ok': False, 'msg': '标签不能为空'})

        tag = obj.tags.filter(name=tag_name).first()
        if tag is None:
            return JsonResponse({'ok': False, 'msg': '该标签不在此条目上'})

        obj.tags.remove(tag)
        return JsonResponse({'ok': True, 'msg': '已移除', 'tag': tag_name})


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
