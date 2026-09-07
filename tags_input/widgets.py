"""Form widgets for tags input."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, ClassVar, cast

from django import forms, urls
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

from .types import TagMapping

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise


class TagsInputWidgetBase(forms.SelectMultiple):
    """Base form widget for tags input rendering and value extraction."""

    mapping: TagMapping
    on_add_tag: str | None
    on_remove_tag: str | None
    on_change_tag: str | None

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        choices: Any = (),
        *,
        on_add_tag: str | None = None,
        on_remove_tag: str | None = None,
        on_change_tag: str | None = None,
    ) -> None:
        """Initialise the widget with optional JS callback hooks.

        The callbacks are keyword-only so that ``attrs`` and ``choices``,
        which Django passes positionally, can never land in them.
        """
        self.on_add_tag = on_add_tag
        self.on_remove_tag = on_remove_tag
        self.on_change_tag = on_change_tag
        self.mapping = cast(TagMapping, {})
        super().__init__(attrs, choices)

    def build_attrs(
        self,
        base_attrs: dict[str, Any] | None,
        extra_attrs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compatibility function for the behaviour changes in Django 1.11+."""
        attrs: dict[str, Any] = dict(base_attrs or {}, **kwargs)
        if extra_attrs:
            attrs.update(extra_attrs)
        return attrs

    def render(
        self,
        name: str,
        value: Any,
        attrs: dict[str, Any] | None = None,
        renderer: Any = None,
    ) -> SafeString:
        """Render the widget as HTML with tag autocompletion and styling."""
        context: dict[str, Any] = self.build_attrs(attrs, name=name)
        context['on_add_tag'] = self.on_add_tag
        context['on_remove_tag'] = self.on_remove_tag
        context['on_change_tag'] = self.on_change_tag

        context['STATIC_URL'] = settings.STATIC_URL
        context['mapping'] = self.mapping
        context['autocomplete_url'] = urls.reverse(
            'tags_input:autocomplete',
            kwargs=dict(
                app=self.mapping['app'],
                model=self.mapping['model'],
                fields='-'.join(self.mapping['fields']),
            ),
        )

        if value:
            fields: Sequence[str] = self.mapping['fields']
            join_func = self.mapping['join_func']

            ids: list[object] = []
            for v in value:
                if hasattr(v, 'pk'):
                    ids.append(v.pk)
                elif isinstance(v, int):
                    ids.append(v)
                elif isinstance(v, str) and v.isdigit():
                    ids.append(int(v))

            values_map: dict[object, str] = dict(
                map(
                    join_func,
                    self.mapping['queryset']
                    .filter(pk__in=ids)
                    .values('pk', *fields),
                )
            )

            values: list[str] = []
            for v in value:
                v_pk: object = getattr(v, 'pk', v)
                if v_pk in values_map:
                    values.append(values_map[v_pk])
                elif (
                    isinstance(v, str) and v.isdigit() and int(v) in values_map
                ):
                    values.append(values_map[int(v)])
                else:
                    values.append(str(v))

            context['values'] = ', '.join(values)

        rendered: str = render_to_string('tags_input_widget.html', context)
        return mark_safe(rendered)

    def value_from_datadict(
        self,
        data: Mapping[str, Any],
        files: Mapping[str, Any],
        name: str,
    ) -> list[str]:
        """Extract cleaned list of tags from form submission data."""
        raw_tags: object = data.get(name, '')
        tags: list[str] = str(raw_tags).split(',')
        incomplete: object = data.get(name + '_incomplete', '')
        if incomplete != data.get(name + '_default'):
            tags += str(incomplete).split(',')
        return [t.strip() for t in tags if t]


class TagsInputWidget(TagsInputWidgetBase):
    """Form widget with bundled CSS and JavaScript assets."""

    class Media:
        """Static media assets for tags input widget."""

        css: ClassVar[dict[str, Sequence[str]]] = {
            'all': ('jquery.tagsinput-revisited-2.0.min.css',),
        }
        js: ClassVar[tuple[str, ...]] = (
            'jquery.tagsinput-revisited-2.0.min.js',
        )
        enable_jquery: bool = getattr(
            settings, 'TAGS_INPUT_INCLUDE_JQUERY', True
        )
        if enable_jquery:
            css['all'] = (*css['all'], 'jquery-ui-1.12.1.min.css')
            js = ('jquery-3.2.1.min.js', 'jquery-ui-1.12.1.min.js', *js)


class AdminTagsInputWidget(TagsInputWidgetBase):
    """Admin widget integrating tags input with Django admin styling.

    The constructor mirrors the admin's ``FilteredSelectMultiple`` so the
    widget can stand in for it, and ``use_fieldset`` matches it so the admin
    renders the label as a ``<legend>`` the same way. Inheriting from it would
    add nothing: the admin only constructs that widget for ``filter_vertical``
    and ``filter_horizontal`` fields and never checks for it.
    """

    use_fieldset: bool = True
    verbose_name: StrOrPromise
    is_stacked: bool

    def __init__(
        self,
        verbose_name: StrOrPromise,
        is_stacked: bool,
        attrs: dict[str, Any] | None = None,
        choices: Any = (),
        *,
        on_add_tag: str | None = None,
        on_remove_tag: str | None = None,
        on_change_tag: str | None = None,
    ) -> None:
        """Initialise the admin widget and its optional JS callback hooks."""
        self.verbose_name = verbose_name
        self.is_stacked = is_stacked
        super().__init__(
            attrs,
            choices,
            on_add_tag=on_add_tag,
            on_remove_tag=on_remove_tag,
            on_change_tag=on_change_tag,
        )

    @property
    def media(self) -> forms.Media:
        """Return combined media assets for admin tags input widget."""
        return forms.Media(js=self.Media.js, css=self.Media.css)

    class Media:
        """Static media assets for admin tags input widget."""

        css: ClassVar[dict[str, Sequence[str]]] = getattr(
            settings,
            'TAGS_INPUT_ADMIN_CSS',
            {
                'all': (
                    'jquery.tagsinput-revisited-2.0.min.css',
                    'jquery-ui-1.12.1.min.css',
                ),
            },
        )
        js: ClassVar[list[str]] = list(
            getattr(
                settings,
                'TAGS_INPUT_ADMIN_JS',
                (
                    'jquery-3.2.1.min.js',
                    'jquery-ui-1.12.1.min.js',
                    'jquery.tagsinput-revisited-2.0.min.js',
                ),
            )
            or ()
        )


__all__: list[str] = [
    'AdminTagsInputWidget',
    'TagsInputWidget',
    'TagsInputWidgetBase',
]
