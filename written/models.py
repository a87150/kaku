from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from django.utils.html import strip_tags

import mistune

from index.models import Tag
from comment.models import Comment


class Article(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(_('title'), max_length=50)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('a_author'), on_delete=models.CASCADE)
    content = models.TextField(_('content'))
    excerpt = models.CharField(_('excerpt'), max_length=100, blank=True, null=True)
    created_time = models.DateTimeField(_('created time'), auto_now_add=True)
    last_modified_time = models.DateTimeField(_('last modified time'), auto_now=True)
    views = models.PositiveIntegerField(_('views'), default=0, editable=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name=_('a_likes'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))
    comments = GenericRelation(Comment, verbose_name=_('comments'))

    class Meta:
        ordering = ['-created_time']
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('written:detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):    
        # 如果没有填写摘要
        if not self.excerpt:
            # 首先实例化一个 Markdown 类，用于渲染 body 的文本
            markdown = mistune.Markdown()
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(markdown(self.content))[:99]+'…'

        # 调用父类的 save 方法将数据保存到数据库中
        super().save(*args, **kwargs)


class Chapter(models.Model):

    title = models.CharField(_('title'), max_length=50)
    content = models.TextField(_('content'))
    created_time = models.DateTimeField(_('created time'), auto_now_add=True)
    last_modified_time = models.DateTimeField(_('last modified time'), auto_now=True)
    article = models.ForeignKey(Article, blank=False, null=False, verbose_name=_('article'), on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('written:chapter', kwargs={'pk': self.pk})