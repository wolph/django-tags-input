"""The same model forms run in the server and the browser worker."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django import forms
from django.db import models
from django.utils.safestring import mark_safe

from tags_input.admin import TagsInputFormMixin
from tags_input.fields import TagsInputField

from .models import Article, Contact, Tag
from .widgets import ShowcaseWidget

if TYPE_CHECKING:
    _ArticleFormBase = forms.ModelForm[models.Model]
else:
    _ArticleFormBase = forms.ModelForm


class CreateForm(TagsInputFormMixin, _ArticleFormBase):
    """Create unknown tag labels while preserving selection order."""

    tags: TagsInputField = TagsInputField(
        Tag.objects.all(),
        create_missing=True,
        required=False,
        widget=ShowcaseWidget(
            on_change_tag=mark_safe('function () { this.trigger("change"); }')
        ),
    )

    class Meta:
        """Expose only this mode's many-to-many field."""

        model: type[Article] = Article
        fields: ClassVar[list[str]] = ['tags']


class ExistingForm(TagsInputFormMixin, _ArticleFormBase):
    """Reject labels absent from the tag catalogue."""

    tags: TagsInputField = TagsInputField(
        Tag.objects.all(),
        required=False,
        widget=ShowcaseWidget(
            on_change_tag=mark_safe('function () { this.trigger("change"); }')
        ),
    )

    class Meta:
        """Expose only this mode's many-to-many field."""

        model: type[Article] = Article
        fields: ClassVar[list[str]] = ['tags']


class CompositeForm(TagsInputFormMixin, _ArticleFormBase):
    """Select existing contacts by their combined names."""

    contacts: TagsInputField = TagsInputField(
        Contact.objects.all(),
        required=False,
        widget=ShowcaseWidget(
            on_change_tag=mark_safe('function () { this.trigger("change"); }')
        ),
    )

    class Meta:
        """Expose only this mode's many-to-many field."""

        model: type[Article] = Article
        fields: ClassVar[list[str]] = ['contacts']


FORMS: dict[
    str, type[CreateForm] | type[ExistingForm] | type[CompositeForm]
] = {
    'create': CreateForm,
    'existing': ExistingForm,
    'composite': CompositeForm,
}
