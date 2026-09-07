"""Public mapping contracts and Django relationship boundaries."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, Protocol, TypedDict

from django.db import models

if TYPE_CHECKING:
    TagQuerySet = models.QuerySet[models.Model]
    ValueQuerySet = models.QuerySet[models.Model, dict[str, object]]


class MappingOptions(TypedDict, total=False):
    """Settings accepted before a model mapping is resolved."""

    field: str
    fields: Sequence[str]
    separator: str
    queryset: TagQuerySet | Callable[[MappingOptions], TagQuerySet]
    create_missing: bool
    split_func: Callable[[str], Mapping[str, object]]
    join_func: Callable[[Mapping[str, object]], tuple[object, str]]
    filter_func: Callable[[Sequence[str]], Mapping[str, object]]
    autocomplete_queryset_filter: Callable[
        [ValueQuerySet, str, str], ValueQuerySet
    ]
    filters: Mapping[str, object]
    excludes: Mapping[str, object]
    ordering: Sequence[str]


class OptionalTagMapping(TypedDict, total=False):
    """Optional settings retained in the resolved mapping."""

    field: str
    create_missing: bool
    autocomplete_queryset_filter: Callable[
        [ValueQuerySet, str, str], ValueQuerySet
    ]
    filters: Mapping[str, object]
    excludes: Mapping[str, object]
    ordering: Sequence[str]


class TagMapping(OptionalTagMapping):
    """Resolved mapping with one-argument label and lookup callbacks."""

    app: str
    model: str
    fields: Sequence[str]
    separator: str
    queryset: TagQuerySet
    split_func: Callable[[str], Mapping[str, object]]
    join_func: Callable[[Mapping[str, object]], tuple[object, str]]
    filter_func: Callable[[Sequence[str]], Mapping[str, object]]


class RelatedTagManager(Protocol):
    """Operations provided by Django's generated many-to-many manager."""

    through: type[models.Model]
    source_field_name: str
    target_field_name: str

    def none(self) -> TagQuerySet:
        """Return an empty queryset for the related model."""
        raise NotImplementedError

    def filter(self, **kwargs: object) -> TagQuerySet:
        """Return related models matching the lookup arguments."""
        raise NotImplementedError

    def clear(self) -> None:
        """Remove all relationships from the owning instance."""
        raise NotImplementedError

    def add(self, *objs: models.Model) -> None:
        """Add relationships to the supplied model instances."""
        raise NotImplementedError


class ModelWithObjects(Protocol):
    """Django models exposing the conventional objects manager."""

    objects: models.Manager[models.Model]
