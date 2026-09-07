"""Form fields for tags input."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, cast

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import utils, widgets
from .types import TagMapping

if TYPE_CHECKING:
    _ModelMultipleChoiceFieldBase = forms.ModelMultipleChoiceField[
        models.Model
    ]
else:
    _ModelMultipleChoiceFieldBase = forms.ModelMultipleChoiceField


class TagsInputField(_ModelMultipleChoiceFieldBase):
    """Form field for tag selection with autocomplete support."""

    widget: type[forms.Widget] = widgets.TagsInputWidget
    default_error_messages: ClassVar[dict[str, Any]] = {
        'list': _('Enter a list of values.'),
        'invalid_choice': _(
            'Select a valid choice. %s is not one of the available choices.'
        ),
        'invalid_pk_value': _('"%s" is not a valid value for a primary key.'),
    }

    create_missing: bool
    mapping: TagMapping | None

    def __init__(
        self,
        queryset: models.QuerySet[models.Model] | None,
        **kwargs: Any,
    ) -> None:
        """Initialise the field and configure the widget mapping."""
        self.create_missing = kwargs.pop('create_missing', False)
        self.mapping = kwargs.pop('mapping', None)
        super().__init__(queryset, **kwargs)
        cast(
            widgets.TagsInputWidgetBase, self.widget
        ).mapping = self.get_mapping()

    def get_mapping(self) -> TagMapping:
        """Retrieve configuration mapping for this field."""
        if not self.mapping:
            assert self.queryset is not None, 'queryset is required'
            mapping: TagMapping = utils.get_mapping(self.queryset)
            mapping['queryset'] = self.queryset
            mapping['create_missing'] = self.create_missing or mapping.get(
                'create_missing', False
            )
            self.mapping = mapping

        return self.mapping

    def clean(self, value: Sequence[str]) -> models.QuerySet[models.Model]:
        """Validate the input tags and return ordered model queryset."""
        assert self.queryset is not None, 'queryset is required'
        mapping: TagMapping = self.get_mapping()
        fields: Sequence[str] = mapping['fields']
        filter_func = mapping['filter_func']
        join_func = mapping['join_func']
        split_func = mapping['split_func']

        filter_kwargs: Mapping[str, object] = filter_func(value)
        values: dict[str, object] = {
            label: pk
            for pk, label in map(
                join_func,
                self.queryset.filter(**filter_kwargs).values('pk', *fields),
            )
        }
        values = {k.lower(): v for k, v in values.items()}
        missing: list[str] = [v for v in value if v.lower() not in values]
        if missing:
            if mapping.get('create_missing', False):
                for v in value:
                    if v in missing:
                        o: models.Model = self.queryset.model(**split_func(v))
                        o.clean()
                        o.save()
                        values[v.lower()] = o.pk
            else:
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': ', '.join(missing)},
                )

        ids: list[object] = [values[v.lower()] for v in value]

        qs: models.QuerySet[models.Model] = super().clean(ids)
        ordered_ids: list[object] = list(dict.fromkeys(ids))
        if ordered_ids:
            from django.db.models import Case, When

            order: Case = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)]
            )
            return qs.order_by(order)
        return qs


class AdminTagsInputField(TagsInputField):
    """Admin form field using the AdminTagsInputWidget."""

    widget: type[forms.Widget] = widgets.AdminTagsInputWidget

    def __init__(
        self,
        queryset: models.QuerySet[models.Model] | None,
        verbose_name: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialise the admin field and set label from verbose_name."""
        super().__init__(queryset, *args, **kwargs)

        if verbose_name:
            self.label = verbose_name


__all__: list[str] = ['AdminTagsInputField', 'TagsInputField']
