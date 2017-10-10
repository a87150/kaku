from django import VERSION, forms
from django.conf import settings
from django.template import Context, loader
from django.forms.utils import flatatt
from django.utils.html import conditional_escape
from django.utils.encoding import force_text as force_unicode

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from pagedown.widgets import PagedownWidget

from .models import Article, Chapter


use_pagedown = getattr(settings, 'USE_PAGEDOWN')


class markdown(PagedownWidget):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ""
        if VERSION < (1, 11):
            final_attrs = self.build_attrs(attrs, name=name)
        else:
            final_attrs = self.build_attrs(attrs, {'name': name})

        if "class" not in final_attrs:
            final_attrs["class"] = ""
        final_attrs["class"] += "textInput form-control wmd-input"
        template = loader.get_template(self.template)
        context = {
            "attrs": flatatt(final_attrs),
            "body": conditional_escape(force_unicode(value)),
            "id": final_attrs["id"],
            "show_preview": self.show_preview,
        }
        context = Context(context) if VERSION < (1, 9) else context
        return template.render(context)
    

class ArticleCreationForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content', 'excerpt', 'tags')

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
        self.fields['excerpt'].label = '摘要'
        self.fields['excerpt'].help_text = '限制100字以内'
        self.fields['tags'].label = 'tags'
        self.fields['tags'].help_text = '选择标签, 可按Ctrl多选'

        if use_pagedown:
            self.fields['content'].widget = markdown()

    def save(self, commit=True):
        if self.user:
            self.instance.author = self.user
        return super().save(commit=commit)


class ArticleEditForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'content', 'excerpt', 'tags')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', '发布'))
        self.fields['title'].label = '标题'
        self.fields['title'].help_text = '限制为50字'
        self.fields['content'].label = '正文'
        self.fields['content'].help_text = '支持 Markdown 语法标记'
        self.fields['excerpt'].label = '摘要'
        self.fields['excerpt'].help_text = '限制100字以内'
        self.fields['tags'].label = 'tags'
        self.fields['tags'].help_text = '选择文章标签'

        if use_pagedown:
            self.fields['content'].widget = markdown()
            
            
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
            self.fields['content'].widget = markdown()
