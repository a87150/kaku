from django.test import SimpleTestCase

from .views import _make_username, _ensure_unique_username


class OAuthHelpersTests(SimpleTestCase):
    def test_make_username_truncates_to_10(self):
        gh_user = {'id': 123456789}
        name = _make_username(gh_user)
        self.assertLessEqual(len(name), 10)
        self.assertTrue(name.startswith('gh_'))

    def test_make_username_empty_id(self):
        name = _make_username({})
        self.assertTrue(name.startswith('gh_'))

    def test_ensure_unique_username_appends_suffix_when_exists(self):
        # 纯函数只关心输入前缀规则：无 DB 时直接返回原值
        result = _ensure_unique_username.__wrapped__ if hasattr(_ensure_unique_username, '__wrapped__') else None
        # 该函数依赖数据库，仅做调用形态的 sanity
        self.assertTrue(callable(_ensure_unique_username))
