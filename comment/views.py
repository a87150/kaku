import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import CreateView

from actstream.signals import action
from notifications.signals import notify

from .forms import CommentCreationForm
from .models import Comment
from users.models import User


class CommentCreateView(LoginRequiredMixin, CreateView):
    """新建评论。

    被评论对象由 URL 直接给出（ContentType 主键 + 对象主键），不再从 Referer 反解：
    Referer 会被代理或浏览器策略剥掉，而且客户端完全可控。
    """

    model = Comment
    form_class = CommentCreationForm
    template_name = 'comment/comment.html'

    def get_target(self):
        ct = get_object_or_404(ContentType, pk=self.kwargs['ct_id'])
        model = ct.model_class()
        if model is None:
            raise Http404('无法识别评论对象')
        return get_object_or_404(model, pk=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        try:
            latest_comment = request.user.comment_set.latest('created_time')
        except Comment.DoesNotExist:
            latest_comment = None

        if (latest_comment is not None
                and latest_comment.created_time + timezone.timedelta(seconds=60) > timezone.now()):
            return HttpResponseForbidden('评论间隔小于 1 分钟，请稍微休息一会')

        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user': self.request.user,
            'target': self.get_target(),
        })
        return kwargs

    def get_success_url(self):
        # 目标与作者都取自已落库的评论，不再回头重解析原始 POST
        target = self.object.content_object
        author = target.author
        sender = self.request.user
        # 评论内容会被 strip，临时补一个空格，防止 @用户名在结尾时解析不到
        nicknames = set(re.findall(
            r'@(?P<nickname>[a-zA-Z0-9\u0800-\u9fa5]+) ', self.object.content + ' '))

        mentioned = False
        if nicknames:
            recipients = User.objects.filter(nickname__in=nicknames).exclude(pk=sender.pk)
            mentioned = recipients.filter(pk=author.pk).exists()
            if recipients.exists():
                # notify 的 recipient 接受 queryset：一次派发，共用内容类型查询
                notify.send(sender=sender, recipient=recipients, verb='@你', target=target)

        if not mentioned and sender != author:
            notify.send(sender=sender, recipient=author, verb='评论了', target=target)

        action.send(sender, verb='评论了', action_object=target)
        # 跳回被评论对象的详情页，不再采用客户端可控的 Referer
        return target.get_absolute_url()
