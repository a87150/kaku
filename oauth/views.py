from django.shortcuts import render, get_object_or_404
from django.views.generic import RedirectView
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.urls import reverse

from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import random

from allauth.account.signals import user_logged_in, user_signed_up

from users.models import User



# 第一步: 请求github第三方登录
def githhub_login(request):
    data = {
        'client_id': settings.GITHUB_CLIENTID,
        'client_secret': settings.GITHUB_CLIENTSECRET,
        'redirect_uri': settings.GITHUB_CALLBACK,
        'state': random.randint(100, 10000),
    }
    github_auth_url = '%s?%s' %(settings.GITHUB_AUTHORIZE_URL, urlencode(data))
    return HttpResponseRedirect(github_auth_url)

# github认证处理
class GithubAuth(RedirectView):
    url = '/'

    def get(self, request, *args, **kwargs):
        template_html = 'account/login.html'

        # 如果申请登陆页面成功后，就会返回code和state
        if 'code' not in request.GET:
            return render(request, template_html)

        code = request.GET('code')
        # 第二步
        # 将得到的code，通过下面的url请求得到access_token
        url = 'https://github.com/login/oauth/access_token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': settings.GITHUB_CLIENTID,
            'client_secret': settings.GITHUB_CLIENTSECRET,
            'code': code,
            'redirect_uri': settings.GITHUB_CALLBACK,
        }

        # 请求参数需要bytes类型
        binary_data = urlencode(data).encode('utf-8')
        # 设置请求返回的数据类型
        headers={'Accept': 'application/json'}
        req = Request(url, binary_data, headers)
        # json是str类型的，将bytes转成str
        result = json.loads(urlopen(req).read().decode('utf-8'))
        access_token = result['access_token']
        url2 = 'https://api.github.com/user?access_token=%s' % (access_token)
        response = json.loads(urlopen(url2).read().decode('utf-8'))
        print(response)
        username = 'gh_' + str(response['id'])
        password = 'jiandandemima1'

        # 如果不存在username，则创建
        try:
            user = User.objects.get(username=username)
        except:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            user_signed_up.send(sender=self, request=request, user=user)

        # 登陆认证
        user = auth.authenticate(username=username, password=password)
        auth.login(request, user, backend=None)
        user_logged_in.send(sender=self, request=request, user=user)
        return super().get(self, request, *args, **kwargs)