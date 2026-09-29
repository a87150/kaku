from django.core.exceptions import ValidationError

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import USERNAME_MAX_LEN
from .receivers import get_ip


class AccountAdapter(DefaultAccountAdapter):
    # 注意：allauth 65 已不再读取 username_regex（字符集由
    # ACCOUNT_USERNAME_VALIDATORS 里的校验器负责），这里只保留长度规则。

    def clean_username(self, username, *args, **kwargs):
        if len(username) > USERNAME_MAX_LEN:
            raise ValidationError("用户名最长为%d个字符" % USERNAME_MAX_LEN)
        return super().clean_username(username, *args, **kwargs)

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.ip_joined = get_ip(request)

        if commit:
            user.save()
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """GitHub 首登建号时同样记录来源 IP。

    社交注册不会走 allauth.account 的 user_signed_up 信号，所以在这里补。
    """

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        if request is not None:
            user.ip_joined = get_ip(request)
            user.save(update_fields=['ip_joined'])
        return user
