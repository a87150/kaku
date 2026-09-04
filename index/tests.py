import json

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from notifications.models import Notification

from index.models import Tag
from index.util import what_type
from kaku.redisfake import patch_redis_down
from written.models import Article
from picture.models import Picture

User = get_user_model()


class IndexPageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pass-1234')

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '欢迎访问kaku')

    def test_home_page_shows_recent_notification_dropdown_data(self):
        """通知下拉小窗依赖 recent_notifications 上下文与未读徽标。"""
        author = User.objects.create_user(username='alice', password='pass-1234')
        Notification.objects.create(
            recipient=self.user, actor=author, verb='评论了',
            description='在《你好》下评论了你', level='info')
        self.client.login(username='bob', password='pass-1234')
        resp = self.client.get('/')
        self.assertContains(resp, '最近通知')
        self.assertContains(resp, '查看详细')
        self.assertContains(resp, '评论了')


class WhatTypeTests(TestCase):
    def test_maps_known_types(self):
        self.assertIs(what_type('article'), Article)
        self.assertIs(what_type('picture'), Picture)

    def test_unknown_type_returns_none(self):
        self.assertIsNone(what_type('novel'))
        self.assertIsNone(what_type(''))
        self.assertIsNone(what_type(None))


class TagCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pass-1234')
        self.article = Article.objects.create(
            author=self.user, title='待加标签的文章', content='正文')

    def post_tag(self, tag='python', type='article', pk=None):
        self.client.login(username='bob', password='pass-1234')
        return self.client.post('/tags/', {
            'tag': tag, 'type': type,
            'pk': pk if pk is not None else self.article.pk})

    def test_requires_login(self):
        resp = self.client.post('/tags/', {'tag': 'x', 'type': 'article',
                                           'pk': self.article.pk})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/users/login/', resp.url)

    def test_add_tag_success(self):
        resp = self.post_tag(tag='python')
        data = json.loads(resp.content)
        self.assertTrue(data['ok'])
        self.assertTrue(self.article.tags.filter(name='python').exists())

    def test_empty_tag_rejected(self):
        resp = self.post_tag(tag='')
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('标签不能为空', data['msg'])

    def test_duplicate_tag_rejected(self):
        self.post_tag(tag='python')
        resp = self.post_tag(tag='python')
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('已添加过该标签', data['msg'])

    def test_unknown_type_rejected(self):
        resp = self.post_tag(type='novel')
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('类型错误', data['msg'])

    def test_missing_object_404(self):
        resp = self.post_tag(pk=99999)
        self.assertEqual(resp.status_code, 404)

    def test_more_than_ten_tags_rejected(self):
        for i in range(10):
            t = Tag.objects.create(name='tag%d' % i)
            self.article.tags.add(t)
        resp = self.post_tag(tag='overflow')
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('超过10个tag', data['msg'])


class LikeCreateViewTests(TestCase):
    def setUp(self):
        cache.clear()
        # 稳定走数据库回退，断言不受本机 Redis 是否运行影响
        self.redis_down = patch_redis_down()
        self.redis_down.start()
        self.addCleanup(self.redis_down.stop)
        self.user = User.objects.create_user(username='bob', password='pass-1234')
        self.article = Article.objects.create(
            author=self.user, title='点赞测试文', content='正文')
        self.picture = Picture.objects.create(
            author=self.user, title='点赞测试图')

    def post_like(self, type, pk, ltype):
        self.client.login(username='bob', password='pass-1234')
        return self.client.post('/like/', {'type': type, 'pk': pk, 'ltype': ltype})

    def test_requires_login(self):
        resp = self.client.post('/like/', {'type': 'article',
                                           'pk': self.article.pk, 'ltype': 'like'})
        self.assertEqual(resp.status_code, 302)

    def test_like_then_dislike_article(self):
        resp = self.post_like('article', self.article.pk, 'like')
        data = json.loads(resp.content)
        self.assertTrue(data['ok'])

        # 点赞后详情页按钮切换为“取消”
        page = self.client.get(self.article.get_absolute_url())
        self.assertContains(page, 'id="dislike-btn"')

        resp = self.post_like('article', self.article.pk, 'dislike')
        data = json.loads(resp.content)
        self.assertTrue(data['ok'])
        page = self.client.get(self.article.get_absolute_url())
        self.assertContains(page, 'id="like-btn"')

    def test_like_picture(self):
        resp = self.post_like('picture', self.picture.pk, 'like')
        data = json.loads(resp.content)
        self.assertTrue(data['ok'])
        page = self.client.get(self.picture.get_absolute_url())
        self.assertContains(page, 'id="dislike-btn"')

    def test_unknown_type_returns_json_error(self):
        """未知类型不应抛 500，而是返回 JSON 错误。"""
        resp = self.post_like('novel', self.article.pk, 'like')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('类型错误', data['msg'])

    def test_like_unknown_object_404(self):
        resp = self.post_like('article', 99999, 'like')
        self.assertEqual(resp.status_code, 404)


class NotificationsListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pass-1234')
        self.alice = User.objects.create_user(username='alice', password='pass-1234')

    def test_requires_login(self):
        resp = self.client.get('/notifications/')
        self.assertEqual(resp.status_code, 302)

    def test_list_shows_notifications(self):
        Notification.objects.create(
            recipient=self.user, actor=self.alice, verb='@你', level='info')
        self.client.login(username='bob', password='pass-1234')
        resp = self.client.get('/notifications/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '通知')
        self.assertContains(resp, '@你')

    def test_empty_state(self):
        self.client.login(username='bob', password='pass-1234')
        resp = self.client.get('/notifications/')
        self.assertContains(resp, '暂时没有通知')

    def test_list_does_not_mark_all_read(self):
        """打开列表不应把全部通知标已读，未读徽标应保留。"""
        n = Notification.objects.create(
            recipient=self.user, actor=self.alice, verb='评论了', level='info')
        self.client.login(username='bob', password='pass-1234')
        self.client.get('/notifications/')
        n.refresh_from_db()
        self.assertTrue(n.unread)

    def test_paginated(self):
        for i in range(12):
            Notification.objects.create(
                recipient=self.user, actor=self.alice,
                verb='动态%d' % i, level='info')
        self.client.login(username='bob', password='pass-1234')
        resp = self.client.get('/notifications/', {'page': 2})
        self.assertEqual(resp.status_code, 200)
