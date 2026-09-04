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

    def test_detail_page_has_toc_container(self):
        """详情页应包含文章目录容器（kaku-toc.js 依标题生成目录）。"""
        article = Article.objects.create(
            author=self.user, title='带小标题的文章',
            content='# 第一章\n\n内容\n\n## 第一节\n\n更多内容')
        resp = self.client.get(article.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'data-toc-for="#content"')
        self.assertContains(resp, 'data-toc-list')

    def test_editor_page_loads_easymde(self):
        """发布页应输出 EasyMDE 编辑器与安全预览所需资源。"""
        self.client.login(username='writer', password='pass-1234')
        resp = self.client.get(reverse('written:create'))
        self.assertEqual(resp.status_code, 200)
        # 编辑器 textarea 由 EasyMDE 接管
        self.assertContains(resp, 'data-md-editor')
        self.assertContains(resp, 'kaku-md-editor')
        # 本地化脚本（EasyMDE / marked / DOMPurify / 初始化）
        self.assertContains(resp, 'vendor/easymde/easymde.min.js')
        self.assertContains(resp, 'vendor/marked/marked.min.js')
        self.assertContains(resp, 'vendor/dompurify/purify.min.js')
        self.assertContains(resp, 'js/kaku-md-init.js')
        # 标签选择器数据注入
        self.assertContains(resp, 'kaku-available-tags')
        self.assertContains(resp, 'kaku-tags-picker')


class ArticleCreateTagTests(TestCase):
    """发布文章时“选择/新建标签”整链路。"""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='writer', password='pass-1234')
        self.client.login(username='writer', password='pass-1234')

    def post_article(self, tags_raw='', **extra):
        data = {
            'title': '标签测试文',
            'content': '正文内容',
            'excerpt': '',
            'tags_raw': tags_raw,
        }
        data.update(extra)
        return self.client.post(reverse('written:create'), data)

    def test_create_with_existing_and_new_tags(self):
        # 预置一个已有标签
        from index.models import Tag
        Tag.objects.create(name='python')
        resp = self.post_article(tags_raw='python, 风景，生活')
        self.assertEqual(resp.status_code, 302)
        article = Article.objects.get(title='标签测试文')
        names = set(article.tags.values_list('name', flat=True))
        self.assertEqual(names, {'python', '风景', '生活'})
        # 新标签已入库
        self.assertTrue(Tag.objects.filter(name='生活').exists())

    def test_create_without_tags(self):
        resp = self.post_article(tags_raw='')
        self.assertEqual(resp.status_code, 302)
        article = Article.objects.get(title='标签测试文')
        self.assertEqual(article.tags.count(), 0)

    def test_too_many_tags_rejected(self):
        many = ', '.join('标签%d' % i for i in range(11))
        resp = self.post_article(tags_raw=many)
        self.assertEqual(resp.status_code, 200)  # 表单重新渲染
        self.assertContains(resp, '标签最多选择 10 个')
        self.assertFalse(Article.objects.filter(title='标签测试文').exists())

    def test_edit_replaces_tags(self):
        from index.models import Tag
        a = Article.objects.create(author=self.user, title='原标题', content='x')
        Tag.objects.create(name='old')
        a.tags.set(Tag.objects.filter(name='old'))
        resp = self.client.post(reverse('written:edit', args=[a.pk]), {
            'title': '改后标题',
            'content': '改后内容',
            'excerpt': '',
            'tags_raw': 'newtag',
        })
        self.assertEqual(resp.status_code, 302)
        a.refresh_from_db()
        self.assertEqual(list(a.tags.values_list('name', flat=True)), ['newtag'])
