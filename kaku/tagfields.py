"""文章/图画表单共用的标签解析与保存工具。

页面标签控件提交的是逗号分隔的标签名字符串（字段名 tags_raw），
服务端据此解析、校验，并把选中的标签名与全站 Tag 表对齐后写回 ManyToMany。
"""
from django.core.exceptions import ValidationError

from index.models import Tag

# 与 index.views.TagCreateView 的“超过10个tag”限制保持一致
MAX_TAGS_PER_ITEM = 10
TAG_NAME_MAX_LEN = Tag._meta.get_field('name').max_length


def parse_tag_names(raw):
    """把 'python, 风景，设计' 之类的输入解析成去重后的标签名列表。"""
    if not raw:
        return []
    names = []
    for chunk in str(raw).replace('，', ',').split(','):
        name = chunk.strip()
        if name and name not in names:
            names.append(name)
    return names


def clean_tag_names(names):
    """标签名集合的通用校验，失败时抛 ValidationError。"""
    if len(names) > MAX_TAGS_PER_ITEM:
        raise ValidationError('标签最多选择 %d 个' % MAX_TAGS_PER_ITEM)
    for name in names:
        if len(name) > TAG_NAME_MAX_LEN:
            raise ValidationError('标签「%s」太长（最多 %d 字）' % (name, TAG_NAME_MAX_LEN))
    return names


def sync_instance_tags(instance, names):
    """把标签名列表同步到 instance.tags（不存在的自动创建），返回 Tag 列表。"""
    tags = [Tag.objects.get_or_create(name=name)[0] for name in names]
    instance.tags.set(tags)
    return tags
