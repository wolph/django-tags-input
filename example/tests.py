from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

import pytest
from django import forms, test
from django.contrib.auth import models as auth_models
from django.db import (
    models as django_models,
    transaction,
)
from django.test import (
    client,
    utils as test_utils,
)

from tags_input import exceptions, fields, utils

from .autocompletionexample import models

if TYPE_CHECKING:
    _ModelFormBase = forms.ModelForm[Any]
else:
    _ModelFormBase = forms.ModelForm

admin_change_url = '/admin/%(app)s/%(model)s/%(id)d/change/'


class Form(forms.Form):
    bar = fields.TagsInputField(
        models.Bar.objects.all(),
    )
    foo = fields.TagsInputField(
        models.Foo.objects.all(),
    )
    bar2 = fields.TagsInputField(
        models.Bar.objects.all(),
        create_missing=True,
    )
    foo2 = fields.TagsInputField(
        models.Foo.objects.all(),
        create_missing=True,
    )


class BaseTestCase(test.TestCase):
    databases: set[str] | Literal['__all__'] = {  # noqa: RUF012
        'default',
        'other',
    }

    @transaction.atomic
    def setUp(self) -> None:
        self.client = client.Client()
        user_mgr: Any = cast(Any, auth_models.User.objects)
        user_mgr.create_superuser(
            'test_user',
            'test@test.com',
            'test',
        )
        self.client.login(
            username='test_user',
            password='test',
        )

        foo = models.Foo.objects.create(name='a')
        bar = models.Bar.objects.create(name='a', foo=foo)
        spam = models.Spam.objects.create(name='a')
        spam.foo.add(foo)
        egg = models.Egg.objects.create(name='a', foo=foo)

        extra_spam = models.ExtraSpam.objects.create(name='a')

        # foo_extra_spam = models.FooExtraSpam.objects.create(
        #     foo=foo, extra_spam=extra_spam)

        assert bar
        assert spam
        assert egg
        assert extra_spam
        # assert foo_extra_spam

    def test_metadata(self) -> None:
        from tags_input import __about__

        assert __about__

    # Utils Test Cases
    def test_get_mapping_type_exception(self) -> None:
        with pytest.raises(TypeError):
            utils.get_mapping(cast(type[django_models.Model], BaseTestCase))

    def test_multiple_fields_mapping(self) -> None:
        utils.get_mapping(models.Egg)

    def test_custom_queryset_mapping(self) -> None:
        utils.get_mapping(models.Spam)

    def test_get_mapping_undefined_exception(self) -> None:
        with pytest.raises(exceptions.MappingUndefined):
            utils.get_mapping(auth_models.User)

    @test_utils.override_settings(
        TAGS_INPUT_MAPPINGS={'autocompletionexample.Foo': {}}
    )
    def test_get_mapping_broken_mappings(self) -> None:
        with pytest.raises(exceptions.ConfigurationError):
            utils.get_mapping(models.Foo)

    # View Test Cases
    def test_view(self) -> None:
        query_params: dict[str, str | int] = {
            'term': 'a',
            'max_results': 5,
        }
        response = self.client.get(
            '/tags_input/autocomplete/autocompletionexample/bar/name/',
            query_params,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/tags_input/autocomplete/autocompletionexample/bar/name/',
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/tags_input/autocomplete/autocompletionexample/bar/name/',
            dict(term='b'),
        )
        self.assertEqual(response.status_code, 200)

    # Admin Test Cases
    def test_admin(self) -> None:
        response = self.client.get(
            admin_change_url
            % dict(app='autocompletionexample', model='bar', id=1)
        )
        self.assertEqual(response.status_code, 200)
        self.client.post(
            '/admin/autocompletionexample/bar/1/',
            response.context['adminform'].form.initial,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            admin_change_url
            % dict(app='autocompletionexample', model='egg', id=1)
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/admin/autocompletionexample/egg/1/',
            response.context['adminform'].form.initial,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        url = admin_change_url % dict(
            app='autocompletionexample', model='foo', id=1
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            url,
            response.context['adminform'].form.initial,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        url = admin_change_url % dict(
            app='autocompletionexample', model='spam', id=1
        )
        response = self.client.get(url)
        data = response.context['adminform'].form.initial.copy()
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        data['foo_incomplete'] = 'a,b,c'
        response = self.client.post(
            admin_change_url
            % dict(app='autocompletionexample', model='spam', id=1),
            data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        url = admin_change_url % dict(
            app='autocompletionexample', model='extraspam', id=1
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            url,
            response.context['adminform'].form.initial,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        url = '/admin/{app}/{model}/add/'.format(
            **dict(app='demo', model='inlinemodel')
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Test Forms
    def test_form(self) -> None:
        form = Form(
            data=dict(
                bar_incomplete='a,b,c',
                bar='abc',
                foo_incomplete='a,b,c',
                foo='abc',
            )
        )
        form.is_valid()

        form = Form(
            data=dict(
                bar_incomplete='a,b,C',
                bar='aBc',
                foo_incomplete='a,B,c',
                foo='Abc',
            )
        )
        form.is_valid()

        form = Form(data=dict(foo='a', bar='a'))
        form['bar'].field.widget.render(name='spam', value='eggs')
        form['bar'].field.widget.render(name='spam', value='')
        form.is_valid()

        form = Form(
            data=dict(
                foo_default='spam',
                foo_incomplete='spam',
                bar_default='spam',
                bar_incomplete='spam',
            )
        )
        form.is_valid()

    def test_widget_callbacks(self) -> None:
        from example.demo import models as demo_models
        from tags_input import widgets

        mapping = utils.get_mapping(demo_models.SimpleName)

        widget = widgets.TagsInputWidget(
            attrs={'class': 'custom'},
            on_add_tag='addTag',
            on_remove_tag='removeTag',
            on_change_tag='changeTag',
        )
        widget.mapping = mapping
        self.assertEqual(widget.attrs, {'class': 'custom'})
        html = widget.render(name='tags', value=[])
        self.assertIn('onAddTag: addTag', html)
        self.assertIn('onRemoveTag: removeTag', html)
        self.assertIn('onChangeTag: changeTag', html)

        # The admin widget goes through FilteredSelectMultiple.__init__, which
        # passes attrs and choices on positionally. They must not end up in
        # the callback slots.
        admin_widget = widgets.AdminTagsInputWidget(
            'Simple names',
            False,
            attrs={'class': 'admin'},
            on_add_tag='addTag',
        )
        admin_widget.mapping = mapping
        self.assertEqual(admin_widget.attrs, {'class': 'admin'})
        self.assertIsNone(admin_widget.on_remove_tag)
        self.assertIsNone(admin_widget.on_change_tag)
        html = admin_widget.render(name='tags', value=[])
        self.assertIn('onAddTag: addTag', html)
        self.assertNotIn('onRemoveTag', html)

    def test_tags_ordering(self) -> None:

        from example.demo import models as demo_models
        from tags_input import widgets

        tag_a = demo_models.SimpleName.objects.create(name='tag_a')
        tag_b = demo_models.SimpleName.objects.create(name='tag_b')
        tag_c = demo_models.SimpleName.objects.create(name='tag_c')

        field = fields.TagsInputField(demo_models.SimpleName.objects.all())
        cleaned = field.clean(['tag_b', 'tag_a', 'tag_c'])
        self.assertEqual(
            list(cleaned.values_list('name', flat=True)),
            ['tag_b', 'tag_a', 'tag_c'],
        )

        widget = widgets.TagsInputWidget()
        widget.mapping = utils.get_mapping(demo_models.SimpleName)

        html = widget.render(name='tags', value=[tag_b, tag_a, tag_c])
        self.assertIn('value="tag_b, tag_a, tag_c"', html)

        html = widget.render(name='tags', value=[tag_b.pk, tag_a.pk, tag_c.pk])
        self.assertIn('value="tag_b, tag_a, tag_c"', html)

        html = widget.render(
            name='tags',
            value=[str(tag_b.pk), str(tag_a.pk), str(tag_c.pk)],
        )
        self.assertIn('value="tag_b, tag_a, tag_c"', html)

        html = widget.render(name='tags', value=['tag_b', 'tag_a', 'tag_c'])
        self.assertIn('value="tag_b, tag_a, tag_c"', html)

        m = demo_models.ManyToManyToSimpleName.objects.create(
            name='test_order'
        )
        url = admin_change_url % dict(
            app='demo', model='manytomanytosimplename', id=m.pk
        )

        response = self.client.post(
            url,
            {'name': 'test_order', 'simple_names': 'tag_b, tag_a, tag_c'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'value="tag_b, tag_a, tag_c"',
            response.content.decode('utf-8'),
        )

        self.assertEqual(
            list(
                cast(
                    django_models.QuerySet[Any],
                    utils.get_tags(m, 'simple_names'),
                ).values_list('name', flat=True)
            ),
            ['tag_b', 'tag_a', 'tag_c'],
        )

        response = self.client.post(
            url,
            {'name': 'test_order', 'simple_names': 'tag_c, tag_b, tag_a'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'value="tag_c, tag_b, tag_a"',
            response.content.decode('utf-8'),
        )

        self.assertEqual(
            list(
                cast(
                    django_models.QuerySet[Any],
                    utils.get_tags(m, 'simple_names'),
                ).values_list('name', flat=True)
            ),
            ['tag_c', 'tag_b', 'tag_a'],
        )

        optional_field = fields.TagsInputField(
            demo_models.SimpleName.objects.all(),
            required=False,
        )
        self.assertEqual(list(optional_field.clean([])), [])

        self.assertEqual(utils.get_tags(tag_a, 'name'), [])
        empty_m = demo_models.ManyToManyToSimpleName.objects.create(
            name='empty'
        )
        self.assertEqual(list(utils.get_tags(empty_m, 'simple_names')), [])

        from django.contrib import admin as django_admin

        from tags_input import admin as tags_input_admin

        site = django_admin.AdminSite()

        class CustomForm(tags_input_admin.TagsInputFormMixin, _ModelFormBase):
            class Meta:
                model = demo_models.ManyToManyToSimpleName
                fields = '__all__'

        admin_instance = tags_input_admin.TagsInputAdmin(
            demo_models.ManyToManyToSimpleName, site
        )
        admin_instance.form = CustomForm
        form_class = admin_instance.get_form(None)
        self.assertTrue(
            issubclass(form_class, tags_input_admin.TagsInputFormMixin)
        )

        class InlineAdmin(tags_input_admin.TagsInputTabularInline):
            model = demo_models.InlineModel
            tag_fields = ('simple_names',)

        inline_admin = InlineAdmin(demo_models.SimpleName, site)
        rf = client.RequestFactory()
        req = rf.get('/')
        user_mgr: Any = cast(Any, auth_models.User.objects)
        user: Any = user_mgr.first()
        assert user is not None
        req.user = user
        formset: Any = inline_admin.get_formset(req)
        formset_form: Any = formset.form
        self.assertTrue(
            issubclass(formset_form, tags_input_admin.TagsInputFormMixin)
        )

        inline_admin.form = type(
            'CustomInlineForm',
            (
                tags_input_admin.TagsInputFormMixin,
                inline_admin.form,
            ),
            {},
        )
        formset2: Any = inline_admin.get_formset(req)
        formset2_form: Any = formset2.form
        self.assertTrue(
            issubclass(formset2_form, tags_input_admin.TagsInputFormMixin)
        )

        class NonTagForm(tags_input_admin.TagsInputFormMixin, _ModelFormBase):
            extra = forms.CharField(required=False)

            class Meta:
                model = demo_models.SimpleName
                fields = ('name',)

        unsaved_form = NonTagForm(instance=demo_models.SimpleName())
        self.assertNotIn('extra', unsaved_form.initial)

        saved_form = NonTagForm(
            data={'name': 'test_clean_save'},
            instance=tag_a,
        )
        self.assertTrue(saved_form.is_valid())
        saved_form.save()

        class CustomThroughForm(
            tags_input_admin.TagsInputFormMixin, _ModelFormBase
        ):
            dummy = fields.TagsInputField(
                demo_models.SimpleName.objects.all(),
                required=False,
            )
            simple_names = fields.TagsInputField(
                demo_models.SimpleName.objects.all(),
                required=False,
            )

            class Meta:
                model = demo_models.ManyToManyThrough
                fields = ('name',)

        m_through = demo_models.ManyToManyThrough.objects.create(
            name='through_test'
        )
        through_form = CustomThroughForm(instance=m_through)
        self.assertNotIn('dummy', through_form.initial)

        through_save_form = CustomThroughForm(
            data={
                'name': 'through_test_save',
                'dummy': 'tag_a',
                'simple_names': 'tag_a',
            },
            instance=m_through,
        )
        self.assertTrue(through_save_form.is_valid())
        through_save_form.save()
