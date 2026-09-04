from django.contrib.auth import get_user_model
from django.test import TestCase

from index.models import Tag
from picture.models import Picture
from written.models import Article

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

    def test_empty_query_page(self):
        resp = self.search()
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '输入关键词开始搜索')

    def test_no_match_message(self):
        resp = self.search(query='不存在的东西')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '没有找到')

    def test_match_article_by_title(self):
        resp = self.search(query='Django')
        self.assertContains(resp, 'Django 教程')

    def test_match_article_by_content(self):
        resp = self.search(query='框架')
        self.assertContains(resp, 'Django 教程')

    def test_match_picture_by_title(self):
        resp = self.search(query='日出')
        self.assertContains(resp, '山间日出')

    def test_type_article_only(self):
        # 关键词同时命中文章标题与图片标题时不适用，这里让关键词只命中图片
        resp = self.search(query='日出', type='article')
        self.assertNotContains(resp, '山间日出')

    def test_type_picture_only(self):
        resp = self.search(query='框架', type='picture')
        self.assertNotContains(resp, 'Django 教程')

    def test_all_includes_both(self):
        other = Article.objects.create(
            author=self.user, title='晨光中的山', content='x')
        resp = self.search(query='山')
        self.assertContains(resp, '山间日出')
        self.assertContains(resp, '晨光中的山')

    def test_match_by_tag(self):
        tag = Tag.objects.create(name='python')
        self.article.tags.add(tag)
        # 标题/正文都不含 python，仅能靠标签命中
        resp = self.search(query='python')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Django 教程')
