from django import forms

from tags_input import fields

from . import models


class TagsInputForm(forms.Form):
    tag_input = fields.TagsInputField(
        models.SimpleName.objects.all(),
        create_missing=True,
        required=True,
    )

