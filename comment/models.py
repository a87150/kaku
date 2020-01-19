from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=300, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


    class Meta:
        ordering = ['-created_time']
    
    def __str__(self):
        return self.content
    
    def increase_likes(self):
        self.likes += 1
        self.save(update_fields=['likes'])
