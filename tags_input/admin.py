"""Django admin integration for tags input."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, ClassVar, cast

from django import forms, http
from django.contrib import admin
from django.contrib.admin import options
from django.db import models

from . import fields, widgets

if TYPE_CHECKING:

    class _TagsInputMixinBase(options.BaseModelAdmin[Any]):
        def get_form(
            self,
            request: http.HttpRequest | None,
            obj: Any = None,
            change: bool = False,
            **kwargs: Any,
        ) -> type[forms.ModelForm[Any]]:
            raise NotImplementedError

        def get_formset(
            self,
            request: http.HttpRequest | None,
            obj: Any = None,
            **kwargs: Any,
        ) -> type[forms.BaseInlineFormSet[Any, Any, Any]]:
            raise NotImplementedError

    class _TagsInputFormMixinBase(forms.BaseModelForm[Any]):
        def _save_m2m(self) -> None:
            raise NotImplementedError

    _ModelAdminBase = admin.ModelAdmin[Any]
    _TabularInlineBase = admin.TabularInline[Any, Any]
    _StackedInlineBase = admin.StackedInline[Any, Any]
else:
    _TagsInputMixinBase = object
    _TagsInputFormMixinBase = object
    _ModelAdminBase = admin.ModelAdmin
    _TabularInlineBase = admin.TabularInline
    _StackedInlineBase = admin.StackedInline


class TagsInputMixin(_TagsInputMixinBase):
    """Admin mixin to enable tags input widgets on ManyToMany fields."""

    tag_fields: ClassVar[Sequence[str] | set[str] | None] = None

    def get_tag_fields(self) -> Sequence[str] | set[str] | None:
        """Get a list of fields on this model that could be potentially tagged.

        By default reads self.tag_fields if it exists or returns None for
        default behaviours.
        """
        return getattr(self, 'tag_fields', None)

    def formfield_for_manytomany(
        self,
        db_field: models.ManyToManyField[Any, Any],
        request: http.HttpRequest | None = None,
        **kwargs: Any,
    ) -> forms.ModelMultipleChoiceField[Any] | None:
        """Get a form Field for a ManyToManyField."""
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        remote_field: Any = db_field.remote_field
        through: Any = remote_field.through
        if not through._meta.auto_created:
            return None

        # If there is a list of taggable fields, and this field isn't one of
        # them, then fall back to parent method.
        tag_fields: Sequence[str] | set[str] | None = self.get_tag_fields()

        if tag_fields and db_field.name not in tag_fields:
            return super().formfield_for_manytomany(
                db_field, request=cast(http.HttpRequest, request), **kwargs
            )

        queryset: models.QuerySet[Any] = (
            db_field.related_model._default_manager.get_queryset()
        )

        kwargs['queryset'] = queryset
        kwargs['widget'] = widgets.AdminTagsInputWidget(
            verbose_name=db_field.verbose_name,
            is_stacked=db_field.name in self.filter_vertical,
            attrs=kwargs.get('attrs'),
            choices=kwargs.get('choices', ()),
        )
        kwargs['required'] = not db_field.blank
        kwargs['help_text'] = getattr(db_field, 'help_text', None)
        kwargs['verbose_name'] = getattr(db_field, 'verbose_name', None)

        # Ugly hack to stop the Django admin from adding the + icon
        if db_field.name not in self.raw_id_fields:
            object.__setattr__(
                self, 'raw_id_fields', (*self.raw_id_fields, db_field.name)
            )

        return cast(
            'forms.ModelMultipleChoiceField[Any]',
            fields.AdminTagsInputField(**kwargs),
        )

    def get_form(
        self,
        request: http.HttpRequest | None,
        obj: Any = None,
        change: bool = False,
        **kwargs: Any,
    ) -> type[forms.ModelForm[Any]]:
        """Get form class wrapped with TagsInputFormMixin."""
        form: type[forms.ModelForm[Any]] = super().get_form(
            request, obj=obj, change=change, **kwargs
        )
        if not issubclass(form, TagsInputFormMixin):
            form = type(form.__name__, (TagsInputFormMixin, form), {})
        return form

    def get_formset(
        self,
        request: http.HttpRequest | None,
        obj: Any = None,
        **kwargs: Any,
    ) -> type[forms.BaseInlineFormSet[Any, Any, Any]]:
        """Get formset class with form wrapped with TagsInputFormMixin."""
        formset: Any = super().get_formset(request, obj=obj, **kwargs)
        if hasattr(formset, 'form') and not issubclass(
            formset.form, TagsInputFormMixin
        ):
            formset.form = type(
                formset.form.__name__,
                (TagsInputFormMixin, formset.form),
                {},
            )
        return cast('type[forms.BaseInlineFormSet[Any, Any, Any]]', formset)


class TagsInputFormMixin(_TagsInputFormMixinBase):
    """Form mixin to preserve order and handle m2m saving for tags input."""

    instance: models.Model
    fields: dict[str, forms.Field]
    cleaned_data: dict[str, Any]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the form and set initial values for tag fields."""
        super().__init__(*args, **kwargs)
        if getattr(self, 'instance', None) and self.instance.pk:
            for field_name, field in self.fields.items():
                if isinstance(field, fields.TagsInputField):
                    manager: Any = getattr(self.instance, field_name, None)
                    if manager and hasattr(manager, 'through'):
                        through: Any = manager.through
                        if through._meta.auto_created:
                            source_field: str = manager.source_field_name
                            target_field: str = manager.target_field_name
                            ordered_pks: list[Any] = list(
                                through.objects.filter(
                                    **{source_field: self.instance}
                                )
                                .order_by('pk')
                                .values_list(target_field, flat=True)
                            )
                            self.initial[field_name] = ordered_pks

    def _save_m2m(self) -> None:
        super()._save_m2m()
        for field_name, field in self.fields.items():
            if (
                isinstance(field, fields.TagsInputField)
                and field_name in self.cleaned_data
            ):
                manager: Any = getattr(self.instance, field_name, None)
                if manager and hasattr(manager, 'through'):
                    through: Any = manager.through
                    if through._meta.auto_created:
                        objs: list[Any] = list(self.cleaned_data[field_name])
                        manager.clear()
                        for obj in objs:
                            manager.add(obj)


class TagsInputAdmin(TagsInputMixin, _ModelAdminBase):
    """Model admin using tags input widgets."""


class TagsInputTabularInline(TagsInputMixin, _TabularInlineBase):
    """Tabular inline admin using tags input widgets."""


class TagsInputStackedInline(TagsInputMixin, _StackedInlineBase):
    """Stacked inline admin using tags input widgets."""


__all__: list[str] = [
    'TagsInputAdmin',
    'TagsInputFormMixin',
    'TagsInputMixin',
    'TagsInputStackedInline',
    'TagsInputTabularInline',
]
