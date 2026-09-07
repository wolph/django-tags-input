"""Exceptions for django-tags-input."""


class TagsInputError(Exception):
    """Base exception for django-tags-input errors."""


class MappingUndefined(TagsInputError):  # noqa: N818
    """Raised when a mapping is undefined for a given model or field."""


class ConfigurationError(Exception):
    """Raised when configuration settings are invalid."""


__all__: list[str] = [
    'ConfigurationError',
    'MappingUndefined',
    'TagsInputError',
]
