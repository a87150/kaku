from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models.signals import post_save

from .mugshot import Avatar


def get_ip(request):
    """取客户端 IP。

    X-Forwarded-For 完全由客户端控制：只有确实部署在可信反向代理之后
    （DJANGO_TRUST_XFF=1）才采信，并且只取第一跳 —— 整串塞进
    GenericIPAddressField 会因为 '1.2.3.4, 5.6.7.8' 非法而写库失败。
    """
    if getattr(settings, 'TRUST_X_FORWARDED_FOR', False):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if forwarded:
            return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def create_default_mugshot(sender, instance, created, **kwargs):
    """新用户自动生成默认头像（只在创建时写一次库）。"""
    if not created or instance.mugshot:
        return

    avatar = Avatar(rows=10, columns=10)
    image_byte_array = avatar.get_image(string=instance.username,
                                        width=480,
                                        height=480,
                                        pad=10)
    instance.mugshot.save('default_mugshot.png', ContentFile(image_byte_array), save=False)
    instance.save(update_fields=['mugshot'])


def record_last_login_ip(sender, request, user, **kwargs):
    """只记录登录 IP。

    原实现同时写 last_login，与 django.contrib.auth 的 update_last_login 重复。
    """
    user.last_login_ip = get_ip(request)
    user.save(update_fields=['last_login_ip'])


def update_joined(sender, request, user, **kwargs):
    user.ip_joined = get_ip(request)
    user.save(update_fields=['ip_joined'])
