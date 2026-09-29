from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxLengthValidator

COMMENT_MAX_LEN = 300


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # TextField 的 max_length 不产生数据库/模型层约束，必须显式挂 validator
    content = models.TextField(max_length=COMMENT_MAX_LEN, blank=True,
                               validators=[MaxLengthValidator(COMMENT_MAX_LEN)])
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
