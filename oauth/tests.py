from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from .views import _ensure_unique_username, _make_username

User = get_user_model()


class MakeUsernameTests(SimpleTestCase):
    def test_truncates_to_10(self):
        name = _make_username({'id': 123456789})
        self.assertLessEqual(len(name), 10)
        self.assertTrue(name.startswith('gh_'))

    def test_empty_id(self):
        name = _make_username({})
        self.assertTrue(name.startswith('gh_'))


class EnsureUniqueUsernameTests(TestCase):
    def test_returns_base_when_free(self):
        self.assertEqual(_ensure_unique_username('gh_123'), 'gh_123')

    def test_appends_suffix_when_taken(self):
        User.objects.create_user(username='gh_123', password='pass-1234')
        result = _ensure_unique_username('gh_123')
        self.assertNotEqual(result, 'gh_123')
        self.assertLessEqual(len(result), 10)
        self.assertFalse(User.objects.filter(username=result).exists())

    def test_keeps_trying_until_free(self):
        for name in ('gh_123', 'gh_1231', 'gh_1232'):
            User.objects.create_user(username=name, password='pass-1234')
        result = _ensure_unique_username('gh_123')
        self.assertLessEqual(len(result), 10)
        self.assertFalse(User.objects.filter(username=result).exists())
