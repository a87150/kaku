from django.contrib.auth import get_user_model
from django.test import TestCase

from .views import _parse_referrer
from written.models import Article
from picture.models import Picture


class ReferrerParseTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='commenter', password='pass-1234')

    def test_parse_written_detail(self):
        article = Article.objects.create(author=self.user, title='A', content='x')
        model, oid = _parse_referrer(
            'http://127.0.0.1:8000/written/article/{}/'.format(article.pk))
        self.assertIs(model, Article)
        self.assertEqual(oid, article.pk)

    def test_parse_picture_detail(self):
        picture = Picture.objects.create(author=self.user, title='P')
        model, oid = _parse_referrer(
            'http://127.0.0.1:8000/picture/picture/{}/'.format(picture.pk))
        self.assertIs(model, Picture)
        self.assertEqual(oid, picture.pk)

    def test_parse_invalid_referrer(self):
        model, oid = _parse_referrer('')
        self.assertIsNone(model)
        self.assertIsNone(oid)

    def test_parse_unknown_page(self):
        model, oid = _parse_referrer('http://127.0.0.1:8000/admin/')
        self.assertIsNone(model)
