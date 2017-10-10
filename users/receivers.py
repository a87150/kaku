from django.utils import timezone


def get_ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    return ip


def update_last_login(sender, request, user, **kwargs):
    user.last_login = timezone.now()
    user.last_login_ip = get_ip(request)
    user.save(update_fields=['last_login', 'last_login_ip'])
    print(user.last_login, user.last_login_ip)


def update_joined(sender, request, user, **kwargs):
    user.ip_joined = get_ip(request)
    user.save(update_fields=['ip_joined'])
    print(user.ip_joined)
