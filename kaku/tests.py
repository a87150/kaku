from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from notifications.models import Notification

from kaku.context_processors import recent_notifications

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
