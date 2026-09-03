import re
from urllib.parse import urlparse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseForbidden
from django.urls import resolve
from django.utils import timezone
from django.views.generic import CreateView

from actstream.signals import action
from notifications.signals import notify

from .forms import CommentCreationForm
from .models import Comment
from users.models import User
from written.models import Article
from picture.models import Picture

# 评论只允许出现在这些内容类型的详情页上（app_name:url_name -> 模型）
COMMENT_TARGETS = {
    ('written', 'detail'): Article,
    ('picture', 'detail'): Picture,
}


def _parse_referrer(referrer):
    """从来源 URL 解析出被评论对象 (model_class, object_id)，解析失败返回 (None, None)。"""
    try:
        path = urlparse(referrer).path
        match = resolve(path)
    except Exception:
        return None, None

    model_class = COMMENT_TARGETS.get((match.app_name, match.url_name))
    object_id = match.kwargs.get('pk')
    if model_class is None or object_id is None:
        return None, None
    return model_class, int(object_id)


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentCreationForm
    template_name = 'comment/comment.html'

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
        referrer = self.request.META.get('HTTP_REFERER', '')

        self.model_class, self.object_id = _parse_referrer(referrer)
        if self.model_class is None:
            raise Http404('无法识别评论对象')

        kwargs.update({
            "user": self.request.user,
            "content_type": ContentType.objects.get_for_model(self.model_class),
            "object_id": self.object_id,
        })
        return kwargs

    def get_success_url(self):
        url = self.referrer = self.request.META.get('HTTP_REFERER', '/')
        # 接受到评论会被 strip，临时为其补一个空格，防止@用户名在最后时无法解析
        comment = (self.request.POST.get('content') or '') + ' '
        nicknames = re.findall(r'@(?P<nickname>[a-zA-Z0-9\u0800-\u9fa5]+) ', comment)
        sender = self.request.user
        target = self.model_class.objects.get(id=self.object_id)
        author = target.author
        mentioned = False

        if nicknames:
            users = User.objects.filter(nickname__in=nicknames)
            if users:
                # 自己 @ 自己不会收到通知
                recipients = users.exclude(id=sender.id)

                if author in recipients:
                    mentioned = True

                for recipient in recipients:
                    notify.send(sender=sender, recipient=recipient, verb='@你', target=target)

        # 如果帖子作者没被 @ 并且回复者不是作者自己，则向作者发送一条通知
        if not mentioned and sender != author:
            notify.send(sender=sender, recipient=author, verb='评论了', target=target)

        action.send(sender, verb='评论了', action_object=target)
        return url
