from django.core.exceptions import ValidationError

import re

from allauth.account.adapter import DefaultAccountAdapter

from .receivers import get_ip


class AccountAdapter(DefaultAccountAdapter):
    username_regex = re.compile(r'^[0-9A-Za-z]+$')

    def clean_username(self, username, *args, **kwargs):
        self.error_messages['invalid_username'] = "用户名只能包含数字和字母"
        if len(username) > 10:
            raise ValidationError("用户名最长为10个字符")
        return super().clean_username(username, *args, **kwargs)

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.ip_joined = get_ip(request)

        if commit:
            user.save()
        return user
