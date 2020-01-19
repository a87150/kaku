from django.db import models
from django.conf import settings
from django.utils import timezone


class Follow(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)
    follow_object = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='follows', on_delete=models.CASCADE)
    started = models.DateTimeField(default=timezone.now)


    class Meta:
        unique_together = ('user', 'follow_object',)
        ordering = ['-started']

    def __str__(self):
        return '%s -> %s' % (self.user, self.follow_object)