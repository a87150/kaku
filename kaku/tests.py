from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from notifications.models import Notification

from kaku.cache import cache_page_anonymous
from kaku.context_processors import recent_notifications
from picture.models import Picture
from written.models import Article, Chapter

User = get_user_model()


class RecentNotificationsContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='bob', password='pass-1234')
        self.alice = User.objects.create_user(username='alice', password='pass-1234')

    def test_anonymous_returns_empty(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        self.assertEqual(recent_notifications(request), {'recent_notifications': []})

    def test_returns_only_own_notifications(self):
        Notification.objects.create(
            recipient=self.user, actor=self.alice, verb='评论了', level='info')
        Notification.objects.create(
            recipient=self.alice, actor=self.user, verb='评论了', level='info')

        request = self.factory.get('/')
        request.user = self.user
        ctx = recent_notifications(request)
        notices = ctx['recent_notifications']
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0].recipient, self.user)

    def test_capped_at_five(self):
        for i in range(7):
            Notification.objects.create(
                recipient=self.user, actor=self.alice,
                verb='动态%d' % i, level='info')

        request = self.factory.get('/')
        request.user = self.user
        notices = recent_notifications(request)['recent_notifications']
        self.assertEqual(len(notices), 5)
        # 最新的在前
        self.assertEqual(notices[0].verb, '动态6')


class CachePageAnonymousTests(TestCase):
    """整页缓存只服务匿名访客。

    已登录渲染含顶栏昵称/头像/未读徽标，一旦进共享缓存就有跨会话串号风险
    （CVE-2026-48588 的触发模式，Django 4.2 无修复版本）。
    """

    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='cacheuser', password='pass-1234')
        self.renders = 0

    def build_view(self):
        @cache_page_anonymous(60)
        def view(request):
            self.renders += 1
            return HttpResponse('第 %d 次渲染' % self.renders)

        return view

    def make_request(self, user):
        request = self.factory.get('/some/list/')
        request.user = user
        return request

    def test_anonymous_requests_hit_the_cache(self):
        view = self.build_view()
        view(self.make_request(AnonymousUser()))
        view(self.make_request(AnonymousUser()))
        self.assertEqual(self.renders, 1)

    def test_authenticated_requests_always_render_fresh(self):
        view = self.build_view()
        view(self.make_request(self.user))
        view(self.make_request(self.user))
        self.assertEqual(self.renders, 2)

    def test_authenticated_response_never_lands_in_shared_cache(self):
        view = self.build_view()
        view(self.make_request(self.user))
        # 若已登录那份被写进缓存，下面这次匿名请求就会命中它，渲染计数不会增加
        view(self.make_request(AnonymousUser()))
        self.assertEqual(self.renders, 2)


class CorePagesSmokeTests(TestCase):
    """核心页面冒烟：把主要路由各请求一遍，确认没有 500 / 模板报错。

    这只能覆盖服务端渲染与路由；点赞、标签增删、画板、编辑器预览/全屏等交互
    仍需在浏览器里实测。
    """

    PUBLIC_PAGES = ['/', '/written/', '/picture/', '/search/', '/search/?query=smoke']
    AUTH_ONLY_PAGES = ['/users/login/', '/users/signup/']
    LOGIN_REQUIRED_PAGES = [
        '/written/new/', '/picture/new/', '/users/profile/',
        '/users/profile/change/', '/users/mugshot/change/',
        '/follow/', '/notifications/',
    ]

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='smoker', password='pass-1234')
        self.article = Article.objects.create(
            author=self.user, title='冒烟文章', content='正文')
        self.chapter = Chapter.objects.create(
            title='冒烟章节', content='章节正文', article=self.article)
        self.picture = Picture.objects.create(
            author=self.user, title='冒烟图画', thematic='pictures/smoke.png')

    def test_public_pages_render(self):
        for url in self.PUBLIC_PAGES + self.AUTH_ONLY_PAGES:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_protected_pages_redirect_anonymous_to_login(self):
        for url in self.LOGIN_REQUIRED_PAGES:
            with self.subTest(url=url):
                resp = self.client.get(url)
                self.assertEqual(resp.status_code, 302)
                self.assertIn('/users/login/', resp.url)

    def test_pages_render_for_logged_in_user(self):
        self.client.login(username='smoker', password='pass-1234')
        urls = self.PUBLIC_PAGES + self.LOGIN_REQUIRED_PAGES + [
            self.article.get_absolute_url(),
            self.chapter.get_absolute_url(),
            self.picture.get_absolute_url(),
            '/users/smoker/',
            '/users/smoker/articles/',
            '/users/smoker/pictures/',
            '/users/smoker/actions/',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)
