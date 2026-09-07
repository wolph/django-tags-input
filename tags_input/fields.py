"""Form fields for tags input."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, cast

from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import utils, widgets

if TYPE_CHECKING:
    _ModelMultipleChoiceFieldBase = forms.ModelMultipleChoiceField[Any]
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
    mapping: dict[str, Any] | None

    def __init__(
        self,
        queryset: models.QuerySet[Any] | None,
        **kwargs: Any,
    ) -> None:
        """Initialize the field and configure the widget mapping."""
        self.create_missing = kwargs.pop('create_missing', False)
        self.mapping = kwargs.pop('mapping', None)
        super().__init__(queryset, **kwargs)
        cast(
            widgets.TagsInputWidgetBase, self.widget
        ).mapping = self.get_mapping()

    def get_mapping(self) -> dict[str, Any]:
        """Retrieve configuration mapping for this field."""
        if not self.mapping:
            assert self.queryset is not None, 'queryset is required'
            mapping: dict[str, Any] = utils.get_mapping(self.queryset)
            mapping['queryset'] = self.queryset
            mapping['create_missing'] = self.create_missing or mapping.get(
                'create_missing', False
            )
            self.mapping = mapping

        return self.mapping

    def clean(self, value: Any) -> models.QuerySet[Any]:
        """Validate the input tags and return ordered model queryset."""
        assert self.queryset is not None, 'queryset is required'
        mapping: dict[str, Any] = self.get_mapping()
        fields: Sequence[str] = mapping['fields']
        filter_func: Callable[..., Any] = mapping['filter_func']
        join_func: Callable[..., Any] = mapping['join_func']
        split_func: Callable[..., Any] = mapping['split_func']

        qs_any: Any = self.queryset
        filter_kwargs: Any = filter_func(value)
        qs_filtered: Any = qs_any.filter(**filter_kwargs)
        qs_values: Any = qs_filtered.values('pk', *fields)
        values: dict[str, Any] = dict(
            join_func(v)[::-1]
            for v in cast(Iterable[Mapping[str, Any]], qs_values)
        )
        values = {k.lower(): v for k, v in values.items()}
        missing: list[str] = [v for v in value if v.lower() not in values]
        if missing:
            if mapping['create_missing']:
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

        ids: list[Any] = [values[v.lower()] for v in value]

        super_clean: Any = super().clean
        qs: models.QuerySet[Any] = cast(
            models.QuerySet[Any],
            super_clean(ids),
        )
        ordered_ids: list[Any] = list(dict.fromkeys(ids))
        if ordered_ids:
            from django.db.models import Case, When

            order: Case = Case(
                *[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)]
            )
            qs_to_order: Any = qs
            ordered_qs: Any = qs_to_order.order_by(order)
            return cast(models.QuerySet[Any], ordered_qs)
        return qs


class AdminTagsInputField(TagsInputField):
    """Admin form field using the AdminTagsInputWidget."""

    widget: type[forms.Widget] = widgets.AdminTagsInputWidget

    def __init__(
        self,
        queryset: models.QuerySet[Any] | None,
        verbose_name: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the admin field and set label from verbose_name."""
        super().__init__(queryset, *args, **kwargs)

        if verbose_name:  # pragma: no branch
            self.label = verbose_name


__all__: list[str] = ['AdminTagsInputField', 'TagsInputField']
