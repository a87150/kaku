from django import forms

from index.models import Tag
from kaku.tagfields import (
    MAX_TAGS_PER_ITEM,
    clean_tag_names,
    parse_tag_names,
    sync_instance_tags,
)

from .models import Picture


class PictureCreateForm(forms.ModelForm):
    """发布图画表单：题图（上传或画板产出）+ 标题 + 标签。

    标签走前端“搜索选择 / 新建”控件，提交为逗号分隔名字（tags_raw）。
    """
    tags_raw = forms.CharField(
        required=False, label='标签', widget=forms.HiddenInput)

    tags_enabled = True

    class Meta:
        model = Picture
        fields = ('title', 'thematic',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'maxlength': 50,
            'placeholder': '给这幅作品起个名字（50 字以内）',
        })
        self.fields['thematic'].widget.attrs.update({
            'class': 'form-control-file',
            'accept': 'image/jpeg,image/png,image/gif,image/webp',
        })
        field = self.fields['tags_raw']
        field.help_text = '支持搜索选择已有标签；输入新标签回车即可，多个标签用逗号分隔（最多 %d 个）' % MAX_TAGS_PER_ITEM

    @property
    def available_tag_names(self):
        if not hasattr(self, '_available_tag_names'):
            self._available_tag_names = list(
                Tag.objects.order_by('name').values_list('name', flat=True))
        return self._available_tag_names

    def clean_tags_raw(self):
        names = clean_tag_names(parse_tag_names(self.cleaned_data.get('tags_raw')))
        return names

    def save(self, commit=True):
        if self.user:
            self.instance.author = self.user
        instance = super().save(commit=commit)
        if commit:
            sync_instance_tags(instance, self.cleaned_data.get('tags_raw') or [])
        return instance
