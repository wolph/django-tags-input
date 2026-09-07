"""Utility functions and mapping handlers for django-tags-input."""

from __future__ import annotations

import functools
from collections.abc import Iterable, Mapping, Sequence
from typing import Any, cast

from django.conf import settings
from django.db import models

from . import exceptions


def get_mappings() -> dict[str, Any]:
    """
    Get all mappings from the settings.

    To use the Django Tags Input module the `TAGS_INPUT_SETTINGS` must be
    defined.
    """
    mappings: dict[str, Any] = getattr(settings, 'TAGS_INPUT_MAPPINGS', {})
    return mappings


def get_mapping(
    model_or_queryset: type[models.Model] | models.QuerySet[Any] | Any,
) -> dict[str, Any]:
    """Get the mapping for a given model or queryset."""
    mappings: dict[str, Any] = get_mappings()

    queryset: models.QuerySet[Any]
    model: type[models.Model]
    if isinstance(model_or_queryset, models.query.QuerySet):
        qs_input: Any = cast(Any, model_or_queryset)
        queryset = cast(models.QuerySet[Any], qs_input)
        model = cast(type[models.Model], qs_input.model)
    elif isinstance(model_or_queryset, type) and issubclass(
        model_or_queryset, models.Model
    ):
        model_cls: Any = model_or_queryset
        queryset = cast(models.QuerySet[Any], model_cls.objects.all())
        model = model_or_queryset
    else:
        raise TypeError(
            'Only `django.db.model.Model` and `django.db.query.QuerySet` '
            'objects are valid arguments'
        )

    model_obj: Any = model
    meta: Any = model_obj._meta
    mapping_key: str = f'{meta.app_label}.{meta.object_name}'

    raw_mapping: dict[str, Any] | None = mappings.get(mapping_key)
    mapping: dict[str, Any]
    if raw_mapping is not None:
        mapping = raw_mapping.copy()
    else:
        raise exceptions.MappingUndefined(
            f'Unable to find mapping for {mapping_key}'
        )

    # The callable allows for customizing the queryset on the fly
    custom_qs: Any = mapping.get('queryset', queryset)
    if callable(custom_qs):
        queryset = cast(models.QuerySet[Any], custom_qs(mapping))
    else:
        queryset = cast(models.QuerySet[Any], custom_qs)

    mapping['app'] = meta.app_label
    mapping['model'] = meta.object_name
    mapping['queryset'] = queryset
    mapping.setdefault('separator', ' - ')

    if 'field' in mapping:
        mapping['fields'] = (mapping['field'],)
    elif 'fields' not in mapping:
        raise exceptions.ConfigurationError(
            'Every mapping should have a field or fields attribute. Mapping: '
            f'{mapping!r}'
        )

    mapping.setdefault(
        'split_func',
        functools.partial(
            mapping.get('split_func', split_func),
            mapping['fields'],
            mapping['separator'],
        ),
    )
    mapping.setdefault(
        'join_func',
        functools.partial(
            mapping.get('join_func', join_func),
            mapping['fields'],
            mapping['separator'],
        ),
    )
    mapping.setdefault(
        'filter_func',
        functools.partial(
            mapping.get('filter_func', filter_func),
            mapping['fields'],
            mapping['separator'],
        ),
    )

    return mapping.copy()


def filter_func(
    fields: Sequence[str],
    separator: str,
    values: Iterable[str] | None,
) -> dict[str, Any]:
    """Build filter kwargs for querying tags across fields."""
    filters: dict[str, Any] = {}
    if values:
        split_values: list[list[str]] = [
            v.split(separator, len(fields)) for v in values
        ]
        items: zip[tuple[str, tuple[str, ...]]] = zip(
            fields, zip(*split_values, strict=False), strict=False
        )
        for field, value in items:
            filters[f'{field}__in'] = value

    return filters


def join_func(
    fields: Sequence[str],
    separator: str,
    values: Mapping[str, Any],
) -> tuple[Any, str]:
    """Combine field values into a formatted tag label."""
    pk: Any = values['pk']
    joined: str = separator.join(str(values[field]) for field in fields)
    return pk, joined


def split_func(
    fields: Sequence[str],
    separator: str,
    value: str,
) -> dict[str, str]:
    """Split a tag label into individual field values."""
    return dict(zip(fields, value.split(separator, len(fields)), strict=False))


def get_tags(
    instance: models.Model,
    field_name: str,
) -> models.QuerySet[Any] | list[Any]:
    """Retrieve ordered tags from a ManyToMany relationship on an instance."""
    manager: Any = getattr(instance, field_name, None)
    if not manager or not hasattr(manager, 'through'):
        return []

    through: Any = manager.through
    source_field: str = manager.source_field_name
    target_field: str = manager.target_field_name
    ordered_pks: list[Any] = list(
        through.objects.filter(**{source_field: instance})
        .order_by('pk')
        .values_list(target_field, flat=True)
    )
    if not ordered_pks:
        return cast(models.QuerySet[Any], manager.none())

    from django.db.models import Case, When

    order: Case = Case(
        *[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_pks)]
    )
    tags_qs: models.QuerySet[Any] = cast(
        models.QuerySet[Any],
        manager.filter(pk__in=ordered_pks).order_by(order),
    )
    return tags_qs


__all__: list[str] = [
    'filter_func',
    'get_mapping',
    'get_mappings',
    'get_tags',
    'join_func',
    'split_func',
]
