from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Field

from .models import Comment

class CommentCreationForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.content_type = kwargs.pop('content_type', None)
        self.object_id = kwargs.pop('object_id', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'comment:create'
        self.helper.form_method = 'post'
        self.helper.form_id = 'comment_create_form'
        self.helper.add_input(Submit('submit', '发布'))
        self.helper.field_class = 'mdui-textfield'
        self.fields['content'].help_text = '限制600字'
        self.helper.layout = Layout(
            Field('content', css_class="mdui-textfield-input", id="content")
        )

    def save(self, commit=True):
        if self.user:
            self.instance.author = self.user
            self.instance.content_type = self.content_type
            self.instance.object_id = self.object_id
        return super().save(commit=commit)
