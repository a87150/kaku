import json
import logging
import secrets

import requests
from django.conf import settings
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import RedirectView

from users.models import User

logger = logging.getLogger(__name__)

GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token'
GITHUB_API_URL = 'https://api.github.com/user'
REQUEST_TIMEOUT = 10


def githhub_login(request):
    """第一步：构造 GitHub OAuth 授权地址并跳转（带 state 防 CSRF）。"""
    if not (settings.GITHUB_CLIENTID and settings.GITHUB_CLIENTSECRET):
        return HttpResponseServerError('GitHub OAuth 未配置：请在 .env 设置 GITHUB_CLIENTID / GITHUB_CLIENTSECRET')

    state = secrets.token_urlsafe(16)
    # 存到 session 供回调校验
    request.session['oauth_state'] = state

    params = {
        'client_id': settings.GITHUB_CLIENTID,
        'redirect_uri': settings.GITHUB_CALLBACK,
        'scope': 'user',
        'state': state,
    }
    url = '{}?{}'.format(
        settings.GITHUB_AUTHORIZE_URL,
        '&'.join('{}={}'.format(k, requests.utils.quote(str(v))) for k, v in params.items()),
    )
    return HttpResponseRedirect(url)


def _make_username(github_user):
    """GitHub 用户映射为站内唯一用户名，保证不超长。"""
    gh_id = str(github_user.get('id', ''))
    base = 'gh_{}'.format(gh_id)
    # 用户名最长 10 字符（与站内注册规则一致）
    return base[:10]


def _ensure_unique_username(base):
    """用户名冲突时追加数字后缀。"""
    candidate = base
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        tail = str(suffix)
        candidate = base[:10 - len(tail)] + tail
        suffix += 1
    return candidate


class GithubAuth(RedirectView):
    """第二步：GitHub 回调，换取 access_token 并登录/创建用户。"""

    url = '/'

    def get(self, request, *args, **kwargs):
        if 'code' not in request.GET:
            return render(request, 'account/login.html')

        # 校验 state，防 CSRF（GitHub 登录状态被伪造）
        expected_state = request.session.get('oauth_state')
        returned_state = request.GET.get('state')
        if not expected_state or returned_state != expected_state:
            logger.warning('GitHub OAuth state 校验失败')
            return HttpResponseRedirect(reverse('account_login'))

        code = request.GET['code']

        # 第二步：code 换取 access_token
        try:
            token_resp = requests.post(
                GITHUB_TOKEN_URL,
                data={
                    'client_id': settings.GITHUB_CLIENTID,
                    'client_secret': settings.GITHUB_CLIENTSECRET,
                    'code': code,
                    'redirect_uri': settings.GITHUB_CALLBACK,
                },
                headers={'Accept': 'application/json'},
                timeout=REQUEST_TIMEOUT,
            )
            token_resp.raise_for_status()
            token_data = token_resp.json()
            access_token = token_data.get('access_token')
            if not access_token:
                logger.error('GitHub 换取 access_token 失败: %s', token_data)
                return HttpResponseRedirect(reverse('account_login'))
        except (requests.RequestException, ValueError) as exc:
            logger.exception('GitHub token 请求异常: %s', exc)
            return HttpResponseRedirect(reverse('account_login'))

        # 第三步：获取用户信息
        try:
            user_resp = requests.get(
                GITHUB_API_URL,
                headers={'Authorization': 'token {}'.format(access_token)},
                timeout=REQUEST_TIMEOUT,
            )
            user_resp.raise_for_status()
            gh_user = user_resp.json()
        except (requests.RequestException, ValueError) as exc:
            logger.exception('GitHub 用户信息请求异常: %s', exc)
            return HttpResponseRedirect(reverse('account_login'))

        base_username = _make_username(gh_user)
        username = _ensure_unique_username(base_username)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 生成随机密码（用户之后只能用 GitHub 登录）
            random_password = secrets.token_urlsafe(24)
            user = User.objects.create_user(username=username, password=random_password)
            user.nickname = gh_user.get('login', username)[:20]
            # 保存昵称（若与已有冲突则用用户名兜底，由模型 save 逻辑保证唯一）
            if not user.nickname:
                user.nickname = username
            user.save()

        # login() 不校验密码，仅建立会话
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth.login(request, user)
        return HttpResponseRedirect(self.url)
