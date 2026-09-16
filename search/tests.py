from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from index.models import Tag
from picture.models import Picture
from written.models import Article

from .templatetags.kaku_highlight import highlight

User = get_user_model()


class SearchViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='searcher', password='pass-1234')
        self.article = Article.objects.create(
            author=self.user, title='Django 教程', content='这是一篇讲框架的文章')
        self.picture = Picture.objects.create(
            author=self.user, title='山间日出')

    def search(self, query='', type='all'):
        params = {}
        if query:
            params['query'] = query
        if type:
            params['type'] = type
        return self.client.get('/search/', params)

    def kinds(self, resp):
        return [item.kaku_kind for item in resp.context['result_list']]

    def test_empty_query_page(self):
        resp = self.search()
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '输入关键词开始搜索')
        self.assertEqual(resp.context['result_count'], 0)

    def test_no_match_message(self):
        resp = self.search(query='不存在的东西')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '没有找到')

    def test_match_article_by_title(self):
        resp = self.search(query='Django')
        self.assertEqual(resp.context['result_count'], 1)
        self.assertEqual(self.kinds(resp), ['文章'])
        self.assertContains(resp, '<mark class="kaku-mark">Django</mark>')

    def test_match_article_by_content(self):
        resp = self.search(query='框架')
        self.assertEqual(resp.context['result_count'], 1)
        # 命中正文时摘要里也要高亮
        self.assertContains(resp, '<mark class="kaku-mark">框架</mark>')

    def test_match_picture_by_title(self):
        resp = self.search(query='日出')
        self.assertEqual(self.kinds(resp), ['图画'])
        self.assertContains(resp, '山间<mark class="kaku-mark">日出</mark>')

    def test_type_article_only(self):
        resp = self.search(query='日出', type='article')
        self.assertEqual(resp.context['result_count'], 0)

    def test_type_picture_only(self):
        resp = self.search(query='框架', type='picture')
        self.assertEqual(resp.context['result_count'], 0)

    def test_all_includes_both(self):
        Article.objects.create(author=self.user, title='晨光中的山', content='x')
        resp = self.search(query='山')
        self.assertIn('图画', self.kinds(resp))
        self.assertIn('文章', self.kinds(resp))

    def test_match_by_tag(self):
        tag = Tag.objects.create(name='python')
        self.article.tags.add(tag)
        # 标题/正文都不含 python，仅能靠标签命中
        resp = self.search(query='python')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['result_count'], 1)

    def test_invalid_type_falls_back_to_all(self):
        resp = self.search(query='山', type='novel')
        self.assertEqual(resp.context['search_type'], 'all')

    def test_query_is_trimmed(self):
        """手机上很容易多打空格，首尾空格不应导致搜不到。"""
        resp = self.search(query='  日出  ')
        self.assertEqual(resp.context['query'], '日出')
        self.assertEqual(resp.context['result_count'], 1)

    def test_results_are_capped_and_flagged(self):
        for i in range(21):
            Article.objects.create(
                author=self.user, title='同类标题%02d' % i, content='x')
        resp = self.search(query='同类标题', type='article')
        self.assertEqual(len(resp.context['result_list']), 20)
        self.assertTrue(resp.context['truncated'])
        self.assertContains(resp, '每类最多展示 20 条')

    def test_not_truncated_when_within_limit(self):
        resp = self.search(query='Django', type='article')
        self.assertFalse(resp.context['truncated'])


class HighlightFilterTests(SimpleTestCase):
    def test_wraps_match_case_insensitively(self):
        self.assertEqual(
            highlight('Django django', 'django'),
            '<mark class="kaku-mark">Django</mark> '
            '<mark class="kaku-mark">django</mark>')

    def test_escapes_html_in_text(self):
        out = highlight('<script>alert(1)</script>', 'alert')
        self.assertNotIn('<script>', out)
        self.assertIn('&lt;script&gt;', out)

    def test_no_query_returns_escaped_text(self):
        self.assertEqual(highlight('<b>x</b>', ''), '&lt;b&gt;x&lt;/b&gt;')

    def test_entities_are_not_split_by_highlight(self):
        # 原文里没有 amp；由转义产生的 &amp; 不该被当成命中切开
        self.assertEqual(highlight('a&b', 'amp'), 'a&amp;b')

    def test_special_regex_chars_treated_literally(self):
        self.assertEqual(
            highlight('a.b', '.'),
            'a<mark class="kaku-mark">.</mark>b')
