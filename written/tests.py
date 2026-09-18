from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from index.models import Tag
from .models import Article
from .views import IndexView


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


class MarkdownRenderTests(TestCase):
    """Markdown 渲染行为契约（编辑器工具栏产出的是 GFM 语法）。"""

    def setUp(self):
        from .views import html_clean
        self.html_clean = html_clean

    def test_gfm_table_rendered_with_alignment(self):
        html = self.html_clean('| 左 | 右 |\n|:--|--:|\n| 1 | 2 |\n')
        self.assertIn('<table', html)
        self.assertIn('<td', html)
        # 对齐由 style 转成安全的 align 属性保留
        self.assertIn('align="left"', html)
        self.assertIn('align="right"', html)

    def test_strikethrough_rendered(self):
        self.assertIn('<del>删除线</del>', self.html_clean('~~删除线~~'))

    def test_script_tag_stripped(self):
        html = self.html_clean('正文<script>alert(1)</script>结束')
        self.assertNotIn('<script', html)

    def test_excerpt_renders_gfm_without_tags(self):
        User = get_user_model()
        user = User.objects.create_user(username='excerptor', password='pass-1234')
        article = Article.objects.create(
            author=user, title='摘要渲染',
            content='| a | b |\n|:--|--:|\n| 1 | 2 |\n\n~~删除~~ 与正文')
        self.assertTrue(article.excerpt.endswith('…'))
        self.assertNotIn('<', article.excerpt)
        self.assertNotIn('|', article.excerpt)  # 表格已渲染成文本而非管道符


class ArticleViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='writer', password='pass-1234')

    def test_written_index_page(self):
        self.client.login(username='writer', password='pass-1234')
        resp = self.client.get(reverse('written:index'))
        self.assertEqual(resp.status_code, 200)

    def test_index_queryset_is_ordered_for_pagination(self):
        """列表页 annotate 聚合后 Meta.ordering 会失效，必须显式排序，否则分页会串数据。"""
        self.assertTrue(IndexView().get_queryset().ordered)

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

    def test_detail_tag_card_allows_inline_edit_for_author(self):
        """详情页标签块带 data-* 供 kaku-tags-live.js 就地增删，作者可见移除按钮。"""
        tag = Tag.objects.create(name='python')
        article = Article.objects.create(author=self.user, title='T', content='body')
        article.tags.add(tag)
        self.client.login(username='writer', password='pass-1234')
        resp = self.client.get(article.get_absolute_url())
        self.assertContains(resp, 'id="kaku-tag-chips"')
        self.assertContains(resp, 'data-tags-type="article"')
        self.assertContains(resp, 'data-tags-pk="%d"' % article.pk)
        self.assertContains(resp, 'data-can-edit="1"')
        self.assertContains(resp, 'class="kaku-tag-remove"')
        self.assertContains(resp, 'js/kaku-tags-live.js')

    def test_detail_tag_card_hides_remove_for_other_users(self):
        """非作者只能看到标签，不能移除。"""
        User = get_user_model()
        tag = Tag.objects.create(name='python')
        article = Article.objects.create(author=self.user, title='T', content='body')
        article.tags.add(tag)
        User.objects.create_user(username='visitor', password='pass-1234')
        self.client.login(username='visitor', password='pass-1234')
        resp = self.client.get(article.get_absolute_url())
        self.assertContains(resp, 'id="kaku-tag-chips"')
        self.assertContains(resp, 'python')
        self.assertNotContains(resp, 'kaku-tag-remove')

    def test_browse_pages_do_not_load_full_site_bootstrap(self):
        """bootstrap 只在表单/评论表单页按需引入，纯浏览页不再全站加载 158KB。"""
        resp = self.client.get(reverse('written:index'))
        self.assertNotContains(resp, 'css/bootstrap.min.css')
        self.assertNotContains(self.client.get('/'), 'css/bootstrap.min.css')

        self.client.login(username='writer', password='pass-1234')
        resp = self.client.get(reverse('written:create'))
        self.assertContains(resp, 'css/bootstrap.min.css')


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
