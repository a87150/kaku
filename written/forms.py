from django import forms
from django.conf import settings

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from pagedown.widgets import PagedownWidget

from .models import Article, Chapter

use_pagedown = getattr(settings, 'USE_PAGEDOWN')

class ArticleCreationForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content', 'tags',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'written:create'
        self.helper.form_method = 'post'
        self.helper.form_id = 'id_create_form'
        self.helper.add_input(Submit('submit', '发布'))
        self.fields['title'].label = '标题'
        self.fields['title'].help_text = '限制为50字'
        self.fields['content'].label = '正文'
        self.fields['content'].help_text = '支持 Markdown 语法标记'
        self.fields['tags'].label = 'tags'
        self.fields['tags'].help_text = '选择标签, 可按Ctrl多选'

        if use_pagedown:
            self.fields['content'].widget = PagedownWidget()

    def save(self, commit=True):
        if self.user:
            self.instance.author = self.user
        return super().save(commit=commit)


class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content', 'tags',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', '发布'))
        self.fields['title'].label = '标题'
        self.fields['title'].help_text = '限制为50字'
        self.fields['content'].label = '正文'
        self.fields['content'].help_text = '支持 Markdown 语法标记'
        self.fields['tags'].label = 'tags'
        self.fields['tags'].help_text = '选择文章标签'

        if use_pagedown:
            self.fields['content'].widget = PagedownWidget()
            
            
class ChapterCreationForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ('title', 'content', 'article',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', '发布'))
        self.fields['title'].label = '标题'
        self.fields['title'].help_text = '限制为50字'
        self.fields['content'].label = '正文'
        self.fields['content'].help_text = '支持 Markdown 语法标记'
        self.fields['article'].label = 'article'
        self.fields['article'].help_text = '选择文章'
        

        if use_pagedown:
            self.fields['content'].widget = PagedownWidget()
