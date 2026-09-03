from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Article


class ArticleModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='writer', password='pass-1234')

    def test_excerpt_auto_generated(self):
        article = Article.objects.create(
            author=self.user,
            title='测试文章',
            content='# 你好\n\n这是一段**很长**的正文，用来测试自动摘要功能是否正常工作。',
        )
        self.assertTrue(article.excerpt)
        self.assertTrue(article.excerpt.endswith('…'))

    def test_html_clean_keeps_table_tags(self):
        from .views import html_clean
        html = html_clean('<table><tr><td>单元格</td></tr></table>')
        self.assertIn('<table', html)
        self.assertIn('<td>单元格</td>', html)


class ArticleViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='writer', password='pass-1234')

    def test_written_index_page(self):
        self.client.login(username='writer', password='pass-1234')
        resp = self.client.get(reverse('written:index'))
        self.assertEqual(resp.status_code, 200)

    def test_article_detail_page(self):
        article = Article.objects.create(author=self.user, title='T', content='body')
        resp = self.client.get(article.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'T')
