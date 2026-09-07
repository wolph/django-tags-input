"""Utility functions and mapping handlers for django-tags-input."""

from __future__ import annotations

import functools
from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, cast

from django.conf import settings
from django.db import models
from django.db.models.options import Options

from . import exceptions
from .types import (
    MappingOptions,
    ModelWithObjects,
    RelatedTagManager,
    TagMapping,
)

if TYPE_CHECKING:
    from .types import TagQuerySet


def get_mappings() -> dict[str, MappingOptions]:
    """
    Get all mappings from the settings.

    To use the Django Tags Input module the `TAGS_INPUT_SETTINGS` must be
    defined.
    """
    mappings: dict[str, MappingOptions] = getattr(
        settings, 'TAGS_INPUT_MAPPINGS', {}
    )
    return mappings


def get_mapping(
    model_or_queryset: object,
) -> TagMapping:
    """Get the mapping for a given model or queryset."""
    mappings: dict[str, MappingOptions] = get_mappings()

    queryset: TagQuerySet
    model: type[models.Model]
    if isinstance(model_or_queryset, models.query.QuerySet):
        queryset = cast('TagQuerySet', model_or_queryset)
        model = queryset.model
    elif isinstance(model_or_queryset, type) and issubclass(
        model_or_queryset, models.Model
    ):
        queryset = cast(ModelWithObjects, model_or_queryset).objects.all()
        model = model_or_queryset
    else:
        raise TypeError(
            'Only `django.db.model.Model` and `django.db.query.QuerySet` '
            'objects are valid arguments'
        )

    meta: Options[models.Model] = model._meta
    mapping_key: str = f'{meta.app_label}.{meta.object_name}'

    raw_mapping: MappingOptions | None = mappings.get(mapping_key)
    mapping: MappingOptions
    if raw_mapping is not None:
        mapping = raw_mapping.copy()
    else:
        raise exceptions.MappingUndefined(
            f'Unable to find mapping for {mapping_key}'
        )

    # The callable allows for customising the queryset on the fly
    custom_qs = mapping.get('queryset', queryset)
    if callable(custom_qs):
        queryset = custom_qs(mapping)
    else:
        queryset = custom_qs

    mapping['queryset'] = queryset
    separator: str = mapping.setdefault('separator', ' - ')

    if 'field' in mapping:
        mapping['fields'] = (mapping['field'],)
    elif 'fields' not in mapping:
        raise exceptions.ConfigurationError(
            'Every mapping should have a field or fields attribute. Mapping: '
            f'{mapping!r}'
        )

    mapping.setdefault(
        'split_func',
        functools.partial(split_func, mapping['fields'], separator),
    )
    mapping.setdefault(
        'join_func',
        functools.partial(join_func, mapping['fields'], separator),
    )
    mapping.setdefault(
        'filter_func',
        functools.partial(filter_func, mapping['fields'], separator),
    )
    # Required keys and callable defaults have now been populated.
    resolved: TagMapping = cast(TagMapping, mapping.copy())
    resolved['app'] = meta.app_label
    resolved['model'] = cast(str, meta.object_name)

    return resolved


def filter_func(
    fields: Sequence[str],
    separator: str,
    values: Iterable[str] | None,
) -> dict[str, object]:
    """Build filter kwargs for querying tags across fields."""
    filters: dict[str, object] = {}
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
    values: Mapping[str, object],
) -> tuple[object, str]:
    """Combine field values into a formatted tag label."""
    pk: object = values['pk']
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
) -> TagQuerySet | list[models.Model]:
    """Retrieve ordered tags from a ManyToMany relationship on an instance."""
    candidate: object = getattr(instance, field_name, None)
    manager: RelatedTagManager = cast(RelatedTagManager, candidate)
    if not manager or not hasattr(manager, 'through'):
        return []

    through: type[models.Model] = manager.through
    source_field: str = manager.source_field_name
    target_field: str = manager.target_field_name
    ordered_pks: list[object] = list(
        cast(ModelWithObjects, through)
        .objects.filter(**{source_field: instance})
        .order_by('pk')
        .values_list(target_field, flat=True)
    )
    if not ordered_pks:
        return manager.none()

    from django.db.models import Case, When

    order: Case = Case(
        *[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_pks)]
    )
    tags_qs: TagQuerySet = manager.filter(pk__in=ordered_pks).order_by(order)
    return tags_qs


__all__: list[str] = [
    'filter_func',
    'get_mapping',
    'get_mappings',
    'get_tags',
    'join_func',
    'split_func',
]
