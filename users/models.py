from django.db import IntegrityError, models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

import os

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


# 站内用户名长度约定（GitHub 派生的 gh_<id> 也必须塞得下），只在这里定义一次
USERNAME_MAX_LEN = 10


def user_mugshot_path(instance, filename):
    return os.path.join('mugshots', instance.username, filename)


class User(AbstractUser):
    last_login_ip = models.GenericIPAddressField(unpack_ipv4=True, blank=True, null=True)
    ip_joined = models.GenericIPAddressField(unpack_ipv4=True, blank=True, null=True)
    nickname = models.CharField(max_length=20, unique=True)
    signature = models.CharField(max_length=200, blank=True)
    mugshot = models.ImageField(upload_to=user_mugshot_path)
    mugshot_thumbnail = ImageSpecField(source='mugshot',
                                       processors=[ResizeToFill(96, 96)],
                                       format='JPEG',
                                       options={'quality': 80})

    def __str__(self):
        return self.nickname

    def _ensure_unique_nickname(self):
        """保证 nickname 唯一：冲突时自动追加数字后缀。"""
        if not self.nickname:
            self.nickname = self.username

        base = self.nickname
        candidate = base
        suffix = 1
        max_len = self._meta.get_field('nickname').max_length
        qs = User.objects.filter(nickname=candidate)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.exists():
            tail = str(suffix)
            candidate = base[: max_len - len(tail)] + tail
            suffix += 1
            qs = User.objects.filter(nickname=candidate)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
        self.nickname = candidate

    def save(self, *args, **kwargs):
        # 注册/导入等未显式提供昵称时，先用用户名兜底；冲突时自动加后缀。
        # 头像生成已挪到 post_save（见 receivers.create_default_mugshot）——
        # save() 应当只是持久化，否则任何一次带 update_fields 的保存都会顺带写文件。
        self._ensure_unique_nickname()
        try:
            super().save(*args, **kwargs)
        except IntegrityError:
            # 两个并发注册可能同时通过唯一性检查，落库时才撞上 unique 约束。
            # 这时另一个事务已提交，再跑一次检查就能拿到带后缀的新昵称。
            self._ensure_unique_nickname()
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('users:detail', args=(self.username,))
        
    class Meta(AbstractUser.Meta):
        pass
        