"""临时冒烟：allauth 65 注册/登录完整流程（用后即删）。"""
import os
import re
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kaku.settings')
django.setup()

from django.test import Client
from django.test.utils import override_settings
from django.contrib.auth import get_user_model

U = get_user_model()
U.objects.filter(username='newbie65').delete()

with override_settings(CAPTCHA_TEST_MODE=True):
    c = Client(HTTP_HOST='127.0.0.1')

    r = c.get('/users/signup/')
    html = r.content.decode('utf-8', 'replace')
    key = re.search(r'name="captcha_0" value="([^"]+)"', html)
    print('signup page:', r.status_code,
          'fields-ok:', all(('name="%s"' % f) in html for f in
                            ['username', 'email', 'password1', 'password2', 'captcha_0', 'captcha_1']))

    r = c.post('/users/signup/', {
        'username': 'newbie65',
        'email': 'newbie65@example.com',
        'password1': 'pass-1234',
        'password2': 'pass-1234',
        'captcha_0': key.group(1) if key else '',
        'captcha_1': 'passed',
    })
    print('signup post:', r.status_code, 'redirect:', r.get('Location', ''))
    user = U.objects.filter(username='newbie65').first()
    print('user created:', bool(user), 'email:', bool(user and user.email),
          'nickname:', user.nickname if user else None)

    # 用户名含非法字符应被我们的 validator 拒绝
    r = c.post('/users/signup/', {
        'username': 'bad name!',
        'email': 'bad@example.com',
        'password1': 'pass-1234',
        'password2': 'pass-1234',
        'captcha_0': key.group(1) if key else '',
        'captcha_1': 'passed',
    })
    bad_html = r.content.decode('utf-8', 'replace')
    print('invalid username rejected:', r.status_code == 200 and '用户名只能包含数字和字母' in bad_html)

    c2 = Client(HTTP_HOST='127.0.0.1')
    print('login by username:', c2.post('/users/login/', {'login': 'newbie65', 'password': 'pass-1234'}).status_code)
    c3 = Client(HTTP_HOST='127.0.0.1')
    print('login by email:', c3.post('/users/login/', {'login': 'newbie65@example.com', 'password': 'pass-1234'}).status_code)

    for path in ['/users/email/', '/users/password/change/', '/users/profile/', '/users/logout/']:
        print('auth page', path, c2.get(path).status_code)

U.objects.filter(username='newbie65').delete()
