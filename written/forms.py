from django import forms

from index.models import Tag
from kaku.tagfields import (
    MAX_TAGS_PER_ITEM,
    clean_tag_names,
    parse_tag_names,
    sync_instance_tags,
)

from .models import Article, Chapter


class ArticleTagMixin:
    """文章创建/编辑表单公用的标签字段与保存逻辑。"""

    #: 让模板知道该表单是否展示“选择/新建标签”控件
    tags_enabled = True

    def _init_tag_field(self):
        field = self.fields['tags_raw']
        field.help_text = '支持搜索选择已有标签；输入新标签回车即可，多个标签用逗号分隔（最多 %d 个）' % MAX_TAGS_PER_ITEM
        # 编辑已有文章时，预填当前标签
        if self.instance and self.instance.pk:
            current = list(self.instance.tags.order_by('name').values_list('name', flat=True))
            field.initial = ', '.join(current)

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
        instance = super().save(commit=commit)
        if commit:
            sync_instance_tags(instance, self.cleaned_data.get('tags_raw') or [])
        return instance


class ArticleCreationForm(ArticleTagMixin, forms.ModelForm):
    tags_raw = forms.CharField(
        required=False, label='标签', widget=forms.HiddenInput)

    class Meta:
        model = Article
        fields = ('title', 'content', 'excerpt')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self._init_tag_field()
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'maxlength': 50,
            'placeholder': '文章标题（50 字以内）',
        })
        self.fields['content'].widget.attrs.update({
            'class': 'form-control kaku-md-editor',
            'data-md-editor': '',
            'rows': 16,
            'placeholder': '在这里用 Markdown 写作…（工具栏可预览 / 全屏）',
        })
        self.fields['excerpt'].widget.attrs.update({
            'class': 'form-control',
            'rows': 2,
            'maxlength': 100,
            'placeholder': '可选：自定义摘要（留空则自动截取正文前 100 字）',
        })

    def save(self, commit=True):
        if self.user:
            self.instance.author = self.user
        return super().save(commit=commit)


class ArticleEditForm(ArticleTagMixin, forms.ModelForm):
    tags_raw = forms.CharField(
        required=False, label='标签', widget=forms.HiddenInput)

    class Meta:
        model = Article
        fields = ('title', 'content', 'excerpt')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._init_tag_field()
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'maxlength': 50,
            'placeholder': '文章标题（50 字以内）',
        })
        self.fields['content'].widget.attrs.update({
            'class': 'form-control kaku-md-editor',
            'data-md-editor': '',
            'rows': 16,
            'placeholder': '在这里用 Markdown 写作…（工具栏可预览 / 全屏）',
        })
        self.fields['excerpt'].widget.attrs.update({
            'class': 'form-control',
            'rows': 2,
            'maxlength': 100,
            'placeholder': '可选：自定义摘要（留空则自动截取正文前 100 字）',
        })


class ChapterCreationForm(forms.ModelForm):
    tags_enabled = False

    class Meta:
        model = Chapter
        fields = ('title', 'content', 'article',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'maxlength': 50,
            'placeholder': '章节标题（50 字以内）',
        })
        self.fields['content'].widget.attrs.update({
            'class': 'form-control kaku-md-editor',
            'data-md-editor': '',
            'rows': 16,
            'placeholder': '在这里用 Markdown 写章节内容…（工具栏可预览 / 全屏）',
        })
        self.fields['article'].widget.attrs.update({'class': 'form-control'})
