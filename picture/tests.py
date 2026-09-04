from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from PIL import Image

from actstream.models import Action

from index.models import Tag
from kaku.redisfake import patch_redis_down
from .models import Picture

User = get_user_model()


def make_png(name='test.png', size=(64, 48), color=(200, 30, 30)):
    """生成一张真实的小 PNG，供 ImageField 校验通过。"""
    buf = BytesIO()
    Image.new('RGB', size, color).save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class PictureListViewTests(TestCase):
    def setUp(self):
        # 列表页套了 cache_page；清空缓存保证每次测试拿到新数据
        cache.clear()
        self.user = User.objects.create_user(username='painter', password='pass-1234')

    def test_index_empty(self):
        resp = self.client.get('/picture/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '暂时还没有图片')

    def test_index_lists_picture_and_lightbox_attrs(self):
        Picture.objects.create(author=self.user, title='第一张画', thematic=make_png())
        resp = self.client.get('/picture/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '第一张画')
        # 灯箱挂载属性：缩略图锚点应带有 data-lightbox*
        self.assertContains(resp, 'data-lightbox')
        self.assertContains(resp, 'data-lightbox-group')

    def test_index_paginates(self):
        for i in range(12):
            Picture.objects.create(
                author=self.user, title='画作%d' % i, thematic=make_png('p%d.png' % i))
        page1 = self.client.get('/picture/')
        self.assertEqual(page1.status_code, 200)
        # 每页 10 张缩略图
        self.assertEqual(page1.content.count(b'kaku-picture-thumb'), 10)

        page2 = self.client.get('/picture/', {'page': 2})
        self.assertEqual(page2.status_code, 200)
        self.assertEqual(page2.content.count(b'kaku-picture-thumb'), 2)


class PictureDetailViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.redis_down = patch_redis_down()
        self.redis_down.start()
        self.addCleanup(self.redis_down.stop)
        self.user = User.objects.create_user(username='painter', password='pass-1234')

    def make_picture(self, **kwargs):
        defaults = dict(author=self.user, title='一幅画', thematic=make_png())
        defaults.update(kwargs)
        return Picture.objects.create(**defaults)

    def test_detail_page(self):
        pic = self.make_picture()
        resp = self.client.get(pic.get_absolute_url())
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '一幅画')
        # 详情页的大图也挂了灯箱
        self.assertContains(resp, 'data-lightbox')

    def test_detail_increments_views(self):
        """浏览计数在渲染后累加：首次显示 0，第二次显示 1，DB 同步为 2。"""
        pic = self.make_picture()
        resp = self.client.get(pic.get_absolute_url())
        self.assertContains(resp, '浏览 0')
        resp = self.client.get(pic.get_absolute_url())
        self.assertContains(resp, '浏览 1')
        pic.refresh_from_db()
        self.assertEqual(pic.views, 2)

    def test_detail_404(self):
        resp = self.client.get('/picture/picture/99999/')
        self.assertEqual(resp.status_code, 404)

    def test_detail_shows_tags_and_comments(self):
        tag = Tag.objects.create(name='风景')
        pic = self.make_picture()
        pic.tags.add(tag)
        resp = self.client.get(pic.get_absolute_url())
        self.assertContains(resp, '风景')
        self.assertContains(resp, '还没有评论')

    def test_detail_like_state_anonymous(self):
        pic = self.make_picture()
        resp = self.client.get(pic.get_absolute_url())
        self.assertContains(resp, '登录后可以点赞')

    def test_detail_like_state_logged_in(self):
        pic = self.make_picture()
        self.client.login(username='painter', password='pass-1234')
        resp = self.client.get(pic.get_absolute_url())
        self.assertContains(resp, 'id="like-btn"')


class PictureCreateViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='painter', password='pass-1234')

    def test_requires_login(self):
        resp = self.client.get('/picture/new/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/users/login/', resp.url)

    def test_get_form_logged_in(self):
        self.client.login(username='painter', password='pass-1234')
        resp = self.client.get('/picture/new/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'picture_create_form')

    def test_create_picture_success(self):
        self.client.login(username='painter', password='pass-1234')
        resp = self.client.post('/picture/new/', {
            'title': '我的新画',
            'thematic': make_png(),
        })
        self.assertEqual(resp.status_code, 302)
        pic = Picture.objects.get(title='我的新画')
        self.assertEqual(pic.author, self.user)
        # actstream 记录了“画了”动态
        self.assertTrue(Action.objects.filter(
            actor_object_id=self.user.pk, verb='画了').exists())
        # 跳到详情页
        self.assertRedirects(resp, pic.get_absolute_url())

    def test_post_frequency_limited(self):
        self.client.login(username='painter', password='pass-1234')
        self.client.post('/picture/new/', {
            'title': '第一张', 'thematic': make_png('a.png')})
        # 6 分钟内再次发图应被拒绝
        resp = self.client.post('/picture/new/', {
            'title': '第二张', 'thematic': make_png('b.png')})
        self.assertEqual(resp.status_code, 403)
        self.assertContains(resp, '发图间隔', status_code=403)
        self.assertEqual(Picture.objects.count(), 1)

    def test_oversized_image_rejected(self):
        self.client.login(username='painter', password='pass-1234')
        # 恰好 1MB，视图按字节数直接拒绝
        big = SimpleUploadedFile('big.png', b'0' * (1024 * 1024),
                                 content_type='image/png')
        resp = self.client.post('/picture/new/', {
            'title': '大图', 'thematic': big})
        self.assertEqual(resp.status_code, 403)
        self.assertContains(resp, '不能大于1mb', status_code=403)
