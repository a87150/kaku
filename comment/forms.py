from django import forms
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Comment


class CommentCreationForm(forms.ModelForm):
    """评论表单。

    target 是被评论的对象，由调用方注入（详情页传当前对象，评论视图从 URL 取），
    不再依赖 Referer。
    """

    class Meta:
        model = Comment
        fields = ('content',)

    def __init__(self, *args, target=None, **kwargs):
        self.user = kwargs.pop('user', None)
        self.target = target
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        if target is not None:
            # crispy 会把这里当 URL 名去 reverse，失败则原样输出；这里直接给路径
            self.helper.form_action = reverse('comment:create', args=[
                ContentType.objects.get_for_model(target).pk, target.pk])
        self.helper.form_method = 'post'
        self.helper.form_id = 'comment_create_form'
        self.helper.add_input(Submit('submit', '发布'))
        self.helper.field_class = 'mdui-textfield'
        self.fields['content'].help_text = '限制300字'
        self.fields['content'].widget.attrs['class']='mdui-textfield-input'
        self.fields['content'].widget.attrs['rows']='1'
        self.fields['content'].widget.attrs['id']='comment-content'

    def save(self, commit=True):
        if self.user:
            self.instance.author = self.user
        if self.target is not None:
            # GenericForeignKey 赋值会同时写 content_type 与 object_id
            self.instance.content_object = self.target
        return super().save(commit=commit)
