from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

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
        self.helper.form_id = 'id_create_form'
        self.helper.add_input(Submit('submit', '发布'))
        self.fields['content'].help_text = '限制500字'

    def save(self, commit=True):
        if self.user:
            self.instance.author = self.user
            self.instance.content_type = self.content_type
            self.instance.object_id = self.object_id
        return super().save(commit=commit)
