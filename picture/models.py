from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse

import os

from index.models import Tag
from comment.models import Comment


def pictures_path(instance, filename):
    return os.path.join('pictures', filename)

class Picture(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(_('title'), max_length=50)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('p_author'), on_delete=models.CASCADE)
    thematic = models.ImageField(_('题图'), upload_to=pictures_path, )
    created_time = models.DateTimeField(_('created_time'), auto_now_add=True)
    views = models.PositiveIntegerField(_('views'), default=0, editable=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name=_('p_likes'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))
    comments = GenericRelation(Comment, verbose_name=_('comments'))

    class Meta:
        ordering = ['-created_time']
        verbose_name = _('Picture')
        verbose_name_plural = _('Pictures')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('picture:detail', kwargs={'pk': self.pk})


class Address(models.Model):

    picture = models.ForeignKey(Picture, blank=False, null=False, verbose_name=_('picture'), on_delete=models.CASCADE)
    address = models.TextField(max_length=6000, verbose_name=_('address'))