from django.contrib.auth.validators import ASCIIUsernameValidator as DjangoASCIIUsernameValidator


class ASCIIUsernameValidator(DjangoASCIIUsernameValidator):
    # 字符集显式写出，与 message 保持一致。
    # Django 的版本用 r'^[\w.@+-]+\Z' + re.ASCII，允许 . @ + - _，
    # 与本项目「只能包含数字和字母」的说法不符。
    regex = r'^[0-9A-Za-z]+\Z'
    message = '用户名只能包含数字和字母'


# allauth 0.63+ 的 ACCOUNT_USERNAME_VALIDATORS 需要一个「指向 list 的路径」，
# 这个 list 里放可调用的校验器（settings 里配置为
# 'users.validators.username_validators'）。
username_validators = [ASCIIUsernameValidator()]
