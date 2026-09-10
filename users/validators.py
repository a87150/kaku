from django.contrib.auth.validators import ASCIIUsernameValidator as DjangoASCIIUsernameValidator


class ASCIIUsernameValidator(DjangoASCIIUsernameValidator):
    regex = r'^[\w]+$'
    message = '用户名只能包含数字和字母'


# allauth 0.63+ 的 ACCOUNT_USERNAME_VALIDATORS 需要一个「指向 list 的路径」，
# 这个 list 里放可调用的校验器（settings 里配置为
# 'users.validators.username_validators'）。
username_validators = [ASCIIUsernameValidator()]
