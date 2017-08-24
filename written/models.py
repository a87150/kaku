from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse

from index.models import Tag
from comment.models import Comment

    
class Article(models.Model):
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(_('title'), max_length=100)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('author'))
    content = models.TextField(_('content'))
    created_time = models.DateTimeField(_('created time'), auto_now_add=True)
    last_modified_time = models.DateTimeField(_('last modified time'), auto_now=True)
    views = models.PositiveIntegerField(_('views'), default=0, editable=False)
    likes = models.PositiveIntegerField(_('likes'), default=0, editable=False)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))
    comments = GenericRelation(Comment, verbose_name=_('comments'))
    
    class Meta:
        ordering = ['-created_time']
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        
    def __str__(self):
        return self.title

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])
        
    def increase_likes(self):
        self.likes += 1
        self.save(update_fields=['likes'])
        
    def get_absolute_url(self):
        return reverse('written:detail', kwargs={'pk': self.pk})

        
class Chapter(models.Model):

    title = models.CharField(_('title'), max_length=100)
    content = models.TextField(_('content'))
    created_time = models.DateTimeField(_('created time'), auto_now_add=True)
    last_modified_time = models.DateTimeField(_('last modified time'), auto_now=True)
    article = models.ForeignKey(Article, blank=False, null=False, verbose_name=_('article'))
    
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse('written:chapter', kwargs={'pk': self.pk})