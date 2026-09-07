"""Mapping callbacks and widget settings retain their public contracts."""

from __future__ import annotations

import importlib
from collections.abc import Mapping, Sequence
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings

from tags_input import fields, utils, widgets
from tags_input.types import MappingOptions, TagMapping

from .autocompletionexample.models import Foo


class MappingContractTests(SimpleTestCase):
    def test_single_argument_callbacks(self) -> None:
        def split(value: str) -> dict[str, str]:
            return {'name': value}

        def join(value: Mapping[str, object]) -> tuple[object, str]:
            return value['pk'], str(value['name'])

        def filter_tags(values: Sequence[str]) -> dict[str, object]:
            return {'name__in': values}

        options: MappingOptions = {
            'field': 'name',
            'split_func': split,
            'join_func': join,
            'filter_func': filter_tags,
        }
        with override_settings(
            TAGS_INPUT_MAPPINGS={'autocompletionexample.Foo': options}
        ):
            mapping: TagMapping = utils.get_mapping(Foo)
        self.assertIs(mapping['split_func'], split)
        self.assertIs(mapping['join_func'], join)
        self.assertIs(mapping['filter_func'], filter_tags)
        self.assertEqual(mapping['split_func']('spam'), {'name': 'spam'})
        self.assertEqual(
            mapping['join_func']({'pk': 1, 'name': 'spam'}), (1, 'spam')
        )
        self.assertEqual(
            mapping['filter_func'](['spam']), {'name__in': ['spam']}
        )
        self.assertNotIn('app', options)

    def test_widget_attribute_precedence(self) -> None:
        widget: widgets.TagsInputWidget = widgets.TagsInputWidget()
        self.assertEqual(
            widget.build_attrs(
                {'class': 'base'}, {'class': 'extra'}, id='tags'
            ),
            {'class': 'extra', 'id': 'tags'},
        )
        self.assertEqual(widget.build_attrs(None), {})

    def test_admin_field_without_verbose_name(self) -> None:
        field: fields.AdminTagsInputField = fields.AdminTagsInputField(
            Foo.objects.all(), widget=widgets.TagsInputWidget()
        )
        self.assertIsNone(field.label)

    def test_media_settings(self) -> None:
        try:
            with override_settings(
                TAGS_INPUT_INCLUDE_JQUERY=False,
                TAGS_INPUT_ADMIN_CSS={'all': ('custom.css',)},
                TAGS_INPUT_ADMIN_JS=('custom.js',),
            ):
                importlib.reload(widgets)
                self.assertEqual(
                    widgets.TagsInputWidget.Media.js,
                    ('jquery.tagsinput-revisited-2.0.min.js',),
                )
                self.assertEqual(
                    widgets.TagsInputWidget.Media.css,
                    {'all': ('jquery.tagsinput-revisited-2.0.min.css',)},
                )
                self.assertEqual(
                    widgets.AdminTagsInputWidget.Media.js, ['custom.js']
                )
                self.assertEqual(
                    widgets.AdminTagsInputWidget.Media.css,
                    {'all': ('custom.css',)},
                )
        finally:
            importlib.reload(widgets)
        self.assertIn('jquery-3.2.1.min.js', widgets.TagsInputWidget.Media.js)


class ManagerContractTests(TestCase):
    def test_mapping_uses_objects_when_default_manager_is_filtered(
        self,
    ) -> None:
        tag: Foo = Foo.objects.create(name='visible through objects')
        with patch.object(Foo._meta, 'default_manager', Foo.objects.none()):
            mapping: TagMapping = utils.get_mapping(Foo)
            self.assertEqual(list(mapping['queryset']), [tag])

    def test_relationship_order_uses_objects_on_through_model(self) -> None:
        from .demo.models import ManyToManyThrough, SimpleName, ThroughModel

        tag: SimpleName = SimpleName.objects.create(name='spam')
        owner: ManyToManyThrough = ManyToManyThrough.objects.create(
            name='owner'
        )
        ThroughModel.objects.create(
            name='relationship', simple_name=tag, many_to_many_through=owner
        )
        with patch.object(
            ThroughModel._meta, 'default_manager', ThroughModel.objects.none()
        ):
            self.assertEqual(
                list(utils.get_tags(owner, 'simple_names')), [tag]
            )


class MediaContractTests(SimpleTestCase):
    def test_none_disables_admin_javascript(self) -> None:
        try:
            with override_settings(TAGS_INPUT_ADMIN_JS=None):
                importlib.reload(widgets)
                widget: widgets.AdminTagsInputWidget = (
                    widgets.AdminTagsInputWidget('tags', False)
                )
                self.assertEqual(list(widget.media.render_js()), [])
        finally:
            importlib.reload(widgets)
