"""Exercise the real Django forms behind both showcases."""

from __future__ import annotations

import json
import string
from typing import Any

import pytest

pytestmark = pytest.mark.django_db


def dispatch(action: str, mode: str = 'create', **kwargs: object) -> Any:
    from showcase.runtime import dispatch_json

    return json.loads(
        dispatch_json(json.dumps(dict(action=action, mode=mode, **kwargs)))
    )


def test_ordered_save_and_reload() -> None:
    assert dispatch('reset')['stored'] == ['Django', 'Python']
    result: Any = dispatch('save', values='Redis, New tag, Django')
    assert result['errors'] == {}
    assert result['stored'] == ['Redis', 'New tag', 'Django']
    assert dispatch('load')['selected'] == result['stored']
    assert '<script' in result['field_html']
    assert dispatch('load', 'existing')['stored'] == ['Django', 'Python']


def test_strict_failure_preserves_storage_and_selection() -> None:
    dispatch('reset')
    result: Any = dispatch('save', 'existing', values='Redis, Unknown')
    assert result['errors']['tags']
    assert result['selected'] == ['Redis', 'Unknown']
    assert result['stored'] == ['Django', 'Python']


def test_composite_and_suggestions() -> None:
    dispatch('reset')
    result: Any = dispatch(
        'save', 'composite', values='Grace - Hopper, Ada - Lovelace'
    )
    assert result['stored'] == ['Grace - Hopper', 'Ada - Lovelace']
    assert dispatch('suggest', 'composite', term='Love') == ['Ada - Lovelace']
    assert dispatch('suggest', term='Py') == ['Python']
    assert dispatch('suggest', term='nonexistent') == []


@pytest.mark.parametrize('mode', ['create', 'existing', 'composite'])
def test_autocomplete_covers_the_alphabet(mode: str) -> None:
    dispatch('reset')
    for letter in string.ascii_lowercase:
        assert dispatch('suggest', mode, term=letter), letter


def test_seed_extends_existing_catalogue_without_changing_selections() -> None:
    from showcase.models import Contact, Tag
    from showcase.seed import seed

    dispatch('reset')
    dispatch('save', values='Redis, Custom tag, Django')
    Tag.objects.exclude(
        name__in=['Django', 'Python', 'PostgreSQL', 'Redis', 'Custom tag']
    ).delete()
    Contact.objects.exclude(first_name__in=['Ada', 'Grace']).delete()
    seed()
    counts: tuple[int, int] = (Tag.objects.count(), Contact.objects.count())
    seed()
    assert (Tag.objects.count(), Contact.objects.count()) == counts
    assert dispatch('load')['stored'] == ['Redis', 'Custom tag', 'Django']
    assert Tag.objects.filter(name__istartswith='z').exists()
    assert Contact.objects.filter(first_name__istartswith='z').exists()


@pytest.mark.parametrize(
    'payload',
    [
        '[]',
        '{}',
        'null',
        '{',
        '{"action":"bad","mode":"create"}',
        '{"action":"load","mode":"bad"}',
        '{"action":"save","mode":"create","values":42}',
        '{"action":"load","mode":"create","extra":true}',
    ],
)
def test_invalid_requests(payload: str) -> None:
    from showcase.runtime import dispatch_json

    with pytest.raises(ValueError):
        dispatch_json(payload)


def test_native_page_and_command() -> None:
    from django.core.management import call_command
    from django.test import Client, override_settings

    call_command('seed_showcase')
    with override_settings(ROOT_URLCONF='showcase.urls'):
        client: Client = Client()
        assert client.get('/').status_code == 200
        response: Any = client.post(
            '/?mode=existing', {'values': 'Redis, Unknown'}
        )
        assert b'Unknown' in response.content
        assert b'csrfmiddlewaretoken' in response.content
        assert client.get('/?mode=invalid').status_code == 400
        assert client.get('/admin/').status_code == 302


def test_empty_save_and_reset_isolation() -> None:
    from example.demo.models import SimpleName
    from showcase.models import Tag

    unrelated: SimpleName = SimpleName.objects.create(name='Keep me')
    dispatch('reset')
    assert dispatch('save', values='')['stored'] == []
    dispatch('save', values='Temporary')
    dispatch('reset')
    assert not Tag.objects.filter(name='Temporary').exists()
    assert SimpleName.objects.filter(pk=unrelated.pk).exists()


@pytest.mark.parametrize(
    'payload',
    [
        42,
        'x' * 16385,
        json.dumps({'action': 'save', 'mode': 'create', 'values': 'x' * 4097}),
        json.dumps({'action': 'suggest', 'mode': 'create', 'term': 'x' * 101}),
        json.dumps({'action': 'save', 'mode': 'create', 'values': 'x' * 101}),
        '[' * 2000,
    ],
)
def test_request_limits(payload: Any) -> None:
    from showcase.runtime import dispatch_json

    with pytest.raises(ValueError):
        dispatch_json(payload)


def test_initialise_invalid_path() -> None:
    from showcase.runtime import initialise

    for path in (None, '', '\x00'):
        with pytest.raises(ValueError):
            initialise(path)


@pytest.mark.django_db(transaction=True)
def test_initialise_existing_database() -> None:
    from showcase.models import Article
    from showcase.runtime import initialise

    initialise(':memory:')
    assert str(Article.objects.get(title='create')) == 'create'


def test_standalone_startup(tmp_path: Any) -> None:
    import os
    import subprocess
    import sys

    import coverage

    env: dict[str, str] = dict(os.environ)
    env.pop('DJANGO_SETTINGS_MODULE', None)
    env['SHOWCASE_TEST_DATABASE'] = str(tmp_path / 'standalone.sqlite3')
    active_coverage: coverage.Coverage | None = coverage.Coverage.current()
    if active_coverage is not None:
        env['SHOWCASE_COVERAGE_FILE'] = active_coverage.config.data_file
    script: str = """
import os
import coverage
from django.db import connections
child_coverage: coverage.Coverage | None = None
if 'SHOWCASE_COVERAGE_FILE' in os.environ:
    child_coverage = coverage.Coverage(
        data_file=os.environ['SHOWCASE_COVERAGE_FILE'], data_suffix=True,
        branch=True, source=['showcase'],
    )
    child_coverage.start()
from showcase.runtime import initialise, dispatch_json
initialise(os.environ['SHOWCASE_TEST_DATABASE'])
initialise(os.environ['SHOWCASE_TEST_DATABASE'])
assert 'Django' in dispatch_json('{"action":"load","mode":"create"}')
connections.close_all()
os.unlink(os.environ['SHOWCASE_TEST_DATABASE'])
initialise(os.environ['SHOWCASE_TEST_DATABASE'])
assert 'Django' in dispatch_json('{"action":"load","mode":"create"}')
connections.close_all()
if child_coverage is not None:
    child_coverage.stop()
    child_coverage.save()
"""
    completed: subprocess.CompletedProcess[str] = subprocess.run(
        [sys.executable, '-c', script],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_native_submits_incomplete_widget_value() -> None:
    from django.test import Client, override_settings

    dispatch('reset')
    with override_settings(ROOT_URLCONF='showcase.urls'):
        response: Any = Client().post(
            '/',
            {
                'tags': 'Django',
                'tags_incomplete': 'New native tag',
                'tags_default': 'Add a tag',
            },
        )
        assert response.status_code == 200
    assert dispatch('load')['stored'] == ['Django', 'New native tag']


@pytest.mark.parametrize('mode', ['create', 'existing', 'composite'])
def test_widget_notifies_host_about_draft_changes(mode: str) -> None:
    dispatch('reset')
    assert 'this.trigger("change")' in dispatch('load', mode)['field_html']


def test_duplicate_new_tags_roll_back_with_field_error() -> None:
    from showcase.models import Tag

    dispatch('reset')
    result: Any = dispatch('save', values='Novel, Novel')
    assert result['errors']['tags'] == [
        'Unable to save this selection. Check for duplicate new tags.'
    ]
    assert result['selected'] == ['Novel', 'Novel']
    assert result['stored'] == ['Django', 'Python']
    assert not Tag.objects.filter(name='Novel').exists()
    assert dispatch('load')['stored'] == ['Django', 'Python']


@pytest.mark.parametrize('label', ['1', '²', '9' * 100])
@pytest.mark.parametrize('mode', ['create', 'existing'])
def test_numeric_labels_render_as_labels(label: str, mode: str) -> None:
    dispatch('reset')
    result: Any = dispatch('save', mode, values=label)
    assert f'value="{label}"' in result['field_html']
    assert result['selected'] == [label]
    if mode == 'create':
        assert result['errors'] == {}
        assert result['stored'] == [label]
        assert f'value="{label}"' in dispatch('load')['field_html']
    else:
        assert result['errors']['tags']
        assert result['stored'] == ['Django', 'Python']


def test_whitespace_only_selection_does_not_create_empty_tag() -> None:
    from showcase.models import Tag

    dispatch('reset')
    result: Any = dispatch('save', values='  ,  , ')
    assert result['stored'] == []
    assert result['selected'] == []
    assert not Tag.objects.filter(name='').exists()


def test_literal_labels_keep_template_escaping() -> None:
    dispatch('reset')
    result: Any = dispatch('save', values='<script>alert("x")</script>')
    assert result['stored'] == ['<script>alert("x")</script>']
    assert (
        'value="&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;"'
        in (result['field_html'])
    )
    assert '<script>alert' not in result['field_html']
