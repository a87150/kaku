"""全局上下文：为每个页面提供最近几条通知，供顶栏通知铃铛下拉面板使用。"""


def recent_notifications(request):
    if not request.user.is_authenticated:
        return {"recent_notifications": []}

    try:
        from notifications.models import Notification

        notices = (
            Notification.objects.filter(recipient=request.user)
            .select_related("actor_content_type")
            .order_by("-timestamp")[:5]
        )
        return {"recent_notifications": list(notices)}
    except Exception:
        return {"recent_notifications": []}
