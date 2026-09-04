import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from actstream.signals import action
from written.models import Article
from .models import Follow

User = get_user_model()


class FollowCreateViewTests(TestCase):
    def setUp(self):
        self.fan = User.objects.create_user(username='fan', password='pass-1234')
        self.star = User.objects.create_user(username='star', password='pass-1234')

    def post_follow(self, object_id, ftype):
        self.client.login(username='fan', password='pass-1234')
        return self.client.post('/follow/create/', {
            'object_id': object_id, 'ftype': ftype})

    def test_requires_login(self):
        resp = self.client.post('/follow/create/', {
            'object_id': self.star.pk, 'ftype': 'follow'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/users/login/', resp.url)

    def test_follow_success(self):
        resp = self.post_follow(self.star.pk, 'follow')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertTrue(data['ok'])
        self.assertTrue(Follow.objects.filter(
            user=self.fan, follow_object=self.star).exists())

    def test_cannot_follow_self(self):
        resp = self.post_follow(self.fan.pk, 'follow')
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('自己', data['msg'])
        self.assertFalse(Follow.objects.filter(user=self.fan).exists())

    def test_duplicate_follow_rejected(self):
        self.post_follow(self.star.pk, 'follow')
        resp = self.post_follow(self.star.pk, 'follow')
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('早已关注', data['msg'])

    def test_unfollow_success(self):
        self.post_follow(self.star.pk, 'follow')
        resp = self.post_follow(self.star.pk, 'unfollow')
        data = json.loads(resp.content)
        self.assertTrue(data['ok'])
        self.assertFalse(Follow.objects.filter(
            user=self.fan, follow_object=self.star).exists())

    def test_unfollow_not_following(self):
        resp = self.post_follow(self.star.pk, 'unfollow')
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('还未关注', data['msg'])

    def test_missing_object_id(self):
        self.client.login(username='fan', password='pass-1234')
        resp = self.client.post('/follow/create/', {'ftype': 'follow'})
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('缺少参数', data['msg'])

    def test_bad_ftype(self):
        resp = self.post_follow(self.star.pk, 'ban')
        data = json.loads(resp.content)
        self.assertFalse(data['ok'])
        self.assertIn('操作类型错误', data['msg'])

    def test_follow_unknown_user(self):
        resp = self.post_follow(99999, 'follow')
        self.assertEqual(resp.status_code, 404)


class FollowListViewTests(TestCase):
    def setUp(self):
        self.fan = User.objects.create_user(username='fan', password='pass-1234')
        self.star = User.objects.create_user(username='star', password='pass-1234')

    def test_requires_login(self):
        resp = self.client.get('/follow/')
        self.assertEqual(resp.status_code, 302)

    def test_empty_stream(self):
        self.client.login(username='fan', password='pass-1234')
        resp = self.client.get('/follow/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '最近 10 天还没有动态')

    def test_stream_contains_followed_actions(self):
        # star 先发一篇文章并产生“写了”动态，fan 再关注 star
        article = Article.objects.create(
            author=self.star, title='被关注者的新文章', content='内容')
        action.send(sender=self.star, verb='写了', action_object=article)
        Follow.objects.create(user=self.fan, follow_object=self.star)

        self.client.login(username='fan', password='pass-1234')
        resp = self.client.get('/follow/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '被关注者的新文章')

    def test_stream_ignores_unfollowed_actions(self):
        article = Article.objects.create(
            author=self.star, title='不应出现的内容', content='内容')
        action.send(sender=self.star, verb='写了', action_object=article)
        self.client.login(username='fan', password='pass-1234')
        resp = self.client.get('/follow/')
        self.assertContains(resp, '最近 10 天还没有动态')
        self.assertNotContains(resp, '不应出现的内容')
