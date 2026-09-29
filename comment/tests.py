from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from notifications.models import Notification

from .models import Comment
from written.models import Article

User = get_user_model()


class CommentCreateTests(TestCase):
    """评论目标由 URL 决定，不再由 Referer 反解。"""

    def setUp(self):
        self.author = User.objects.create_user(username='author', password='pass-1234')
        self.other = User.objects.create_user(username='other', password='pass-1234')
        self.article = Article.objects.create(author=self.author, title='A', content='x')

    def target_url(self, obj):
        return reverse('comment:create', args=[
            ContentType.objects.get_for_model(obj).pk, obj.pk])

    def post_comment(self, obj, content='好文', referer=None):
        self.client.login(username='other', password='pass-1234')
        extra = {'HTTP_REFERER': referer} if referer else {}
        return self.client.post(self.target_url(obj), {'content': content}, **extra)

    def test_comment_attaches_to_url_target(self):
        resp = self.post_comment(self.article)
        self.assertEqual(resp.status_code, 302)
        comment = Comment.objects.get()
        self.assertEqual(comment.content_object, self.article)
        self.assertEqual(comment.author, self.other)

    def test_referer_cannot_redirect_offsite(self):
        """Referer 曾经直接当跳转地址用，是开放重定向。"""
        resp = self.post_comment(self.article, referer='https://evil.com/')
        self.assertEqual(resp['Location'], self.article.get_absolute_url())

    def test_unknown_content_type_is_404(self):
        self.client.login(username='other', password='pass-1234')
        resp = self.client.post(reverse('comment:create', args=[99999, 1]),
                                {'content': 'x'})
        self.assertEqual(resp.status_code, 404)

    def test_missing_target_object_is_404(self):
        self.client.login(username='other', password='pass-1234')
        url = reverse('comment:create', args=[
            ContentType.objects.get_for_model(self.article).pk, 99999])
        resp = self.client.post(url, {'content': 'x'})
        self.assertEqual(resp.status_code, 404)

    def test_requires_login(self):
        resp = self.client.post(self.target_url(self.article), {'content': 'x'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/users/login/', resp.url)

    def test_author_is_notified(self):
        self.post_comment(self.article)
        self.assertTrue(Notification.objects.filter(
            recipient=self.author, verb='评论了').exists())

    def test_mention_replaces_plain_comment_notification(self):
        self.post_comment(self.article, content='@author 你好')
        self.assertTrue(Notification.objects.filter(
            recipient=self.author, verb='@你').exists())
        self.assertFalse(Notification.objects.filter(
            recipient=self.author, verb='评论了').exists())

    def test_comment_interval_limited(self):
        self.post_comment(self.article, content='first')
        resp = self.post_comment(self.article, content='second')
        self.assertEqual(resp.status_code, 403)


class CommentFormActionTests(TestCase):
    def test_detail_page_form_posts_to_target_url(self):
        user = User.objects.create_user(username='writer', password='pass-1234')
        article = Article.objects.create(author=user, title='A', content='x')
        self.client.login(username='writer', password='pass-1234')
        resp = self.client.get(article.get_absolute_url())
        expected = reverse('comment:create', args=[
            ContentType.objects.get_for_model(article).pk, article.pk])
        self.assertContains(resp, 'action="%s"' % expected)

    def test_comment_form_without_target_renders(self):
        from .forms import CommentCreationForm
        self.assertIn('comment-content', str(CommentCreationForm()))
