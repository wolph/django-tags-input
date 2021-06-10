import pytest

from .autocompletionexample import models
import django
from django.db import transaction
from django import forms, test
from django.contrib.auth import models as auth_models
from django.test import client, utils as test_utils
from tags_input import exceptions, utils, fields


if django.VERSION >= (1, 9, 0, '', 0):
    admin_change_url = '/admin/%(app)s/%(model)s/%(id)d/change/'
else:
    admin_change_url = '/admin/%(app)s/%(model)s/%(id)d/'


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
    databases = ['default', 'other']

    @transaction.atomic
    def setUp(self):
        self.client = client.Client()
        auth_models.User.objects.create_superuser(
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

    def test_metadata(self):
        from tags_input import __about__
        assert __about__

    # Utils Test Cases
    @pytest.mark.xfail(raises=TypeError)
    def test_get_mapping_type_exception(self):
        utils.get_mapping(BaseTestCase)

    def test_multiple_fields_mapping(self):
        utils.get_mapping(models.Egg)

    def test_custom_queryset_mapping(self):
        utils.get_mapping(models.Spam)

    @pytest.mark.xfail(raises=exceptions.MappingUndefined)
    def test_get_mapping_undefined_exception(self):
        utils.get_mapping(auth_models.User)

    @pytest.mark.xfail(raises=exceptions.ConfigurationError)
    @test_utils.override_settings(
        TAGS_INPUT_MAPPINGS={'autocompletionexample.Foo': {}})
    def test_get_mapping_broken_mappings(self):
        utils.get_mapping(models.Foo)

    # View Test Cases
    def test_view(self):
        response = self.client.get(
            '/tags_input/autocomplete/autocompletionexample/bar/name/',
            dict(
                term='a',
                max_results=5,
            ),
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
    def test_admin(self):
        response = self.client.get(admin_change_url % dict(
            app='autocompletionexample', model='bar', id=1))
        self.assertEqual(response.status_code, 200)
        self.client.post(
            '/admin/autocompletionexample/bar/1/',
            response.context['adminform'].form.initial,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(admin_change_url % dict(
            app='autocompletionexample', model='egg', id=1))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            '/admin/autocompletionexample/egg/1/',
            response.context['adminform'].form.initial,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        url = admin_change_url % dict(
            app='autocompletionexample', model='foo', id=1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            url,
            response.context['adminform'].form.initial,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        url = admin_change_url % dict(
            app='autocompletionexample', model='spam', id=1)
        response = self.client.get(url)
        data = response.context['adminform'].form.initial.copy()
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        data['foo_incomplete'] = 'a,b,c'
        response = self.client.post(
            admin_change_url % dict(
                app='autocompletionexample', model='spam', id=1),
            data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        url = admin_change_url % dict(
            app='autocompletionexample', model='extraspam', id=1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            url,
            response.context['adminform'].form.initial,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        url = '/admin/%(app)s/%(model)s/add/' % dict(app='demo',
                                                     model='inlinemodel')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Test Forms
    def test_form(self):
        form = Form(data=dict(
            bar_incomplete='a,b,c',
            bar='abc',
            foo_incomplete='a,b,c',
            foo='abc',
        ))
        form.is_valid()

        form = Form(data=dict(
            bar_incomplete='a,b,C',
            bar='aBc',
            foo_incomplete='a,B,c',
            foo='Abc',
        ))
        form.is_valid()

        form = Form(data=dict(foo='a', bar='a'))
        form['bar'].field.widget.render(name='spam', value='eggs')
        form['bar'].field.widget.render(name='spam', value='')
        form.is_valid()

        form = Form(data=dict(
            foo_default='spam',
            foo_incomplete='spam',
            bar_default='spam',
            bar_incomplete='spam',
        ))
        form.is_valid()
