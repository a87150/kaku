from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    """User 模型：nickname 默认与唯一化、保存带默认头像。"""

    def test_create_user_defaults_nickname(self):
        user = User.objects.create_user(username='alice', password='pass-1234')
        self.assertEqual(user.nickname, 'alice')
        self.assertTrue(user.mugshot)  # 自动生成默认头像

    def test_nickname_conflict_does_not_crash(self):
        # 第一个用户 nickname=alice（来自 username）
        User.objects.create_user(username='alice', password='pass-1234')
        # 第二个用户显式把 nickname 设为已占用的 alice，应自动加后缀而不是崩溃
        u2 = User.objects.create_user(username='alice2', password='pass-5678')
        u2.nickname = 'alice'
        u2.save()
        self.assertNotEqual(u2.nickname, 'alice')
        self.assertTrue(u2.nickname.startswith('alice'))
