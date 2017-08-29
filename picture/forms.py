from django import forms
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Picture, Address


class PictureCreateForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ('title', 'thematic', 'tags', )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = 'picture:create'
        self.helper.form_method = 'post'
        self.helper.form_id = 'id_create_form'
        self.helper.add_input(Submit('submit', '发布'))
        self.fields['title'].label = '标题'
        self.fields['title'].help_text = '限制为50字'
        self.fields['thematic'].label = '题图'
        self.fields['tags'].label = 'tags'
        self.fields['tags'].help_text = '选择标签, 可按Ctrl多选'
        
    def save(self, commit=True):
        if self.user:
            self.instance.author = self.user
        return super().save(commit=commit)