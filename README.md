<div align="center">

# Django Tags Input

**Ordered, autocompleting tag inputs for Django `ManyToManyField`s, in your forms and in the admin.**

[![PyPI version](https://img.shields.io/pypi/v/django-tags-input.svg?logo=pypi&logoColor=white)](https://pypi.python.org/pypi/django-tags-input)
[![Python versions](https://img.shields.io/pypi/pyversions/django-tags-input.svg?logo=python&logoColor=white)](https://pypi.python.org/pypi/django-tags-input)
[![Django versions](https://img.shields.io/pypi/frameworkversions/django/django-tags-input.svg?logo=django&logoColor=white)](https://pypi.python.org/pypi/django-tags-input)
[![CI](https://github.com/WoLpH/django-tags-input/actions/workflows/ci.yml/badge.svg)](https://github.com/WoLpH/django-tags-input/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](https://github.com/WoLpH/django-tags-input/actions/workflows/ci.yml)
[![Typed](https://img.shields.io/badge/typed-mypy%20%7C%20pyright%20%7C%20pyrefly-blue.svg)](https://github.com/WoLpH/django-tags-input)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/pypi/l/django-tags-input.svg)](https://github.com/WoLpH/django-tags-input/blob/develop/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/django-tags-input.svg?logo=pypi&logoColor=white)](https://pypi.python.org/pypi/django-tags-input)

[**Documentation**](https://django-tags-input.readthedocs.io/en/latest/) ·
[**PyPI**](https://pypi.python.org/pypi/django-tags-input) ·
[**Source**](https://github.com/WoLpH/django-tags-input) ·
[**Issues**](https://github.com/WoLpH/django-tags-input/issues)

</div>

---

Django Tags Input replaces the stock multiple-select for `ManyToManyField`s
with a tag box: type a few letters, pick a match from the autocomplete list,
and the related object is linked. Point it at a model, tell it which field
holds the label, and the form field, the widget, the autocomplete view and the
admin integration are all wired for you.

<img src="https://raw.githubusercontent.com/WoLpH/django-tags-input/develop/docs/_static/admin-autocomplete.png" alt="The Django admin change form with a tags input showing two selected tags and an open autocomplete list" width="900">

## Highlights

- **Keeps your order.** Enter `B, A, C` and you get `B, A, C` back, both in
  the widget and from `utils.get_tags()`. Django's own `ManyToManyField` API
  gives you database order, which is usually insertion order until it isn't.
- **Autocomplete out of the box.** One URL include serves JSON suggestions
  for every mapped model, filtered with `istartswith` on the label fields.
- **Create missing objects on the fly.** Set `create_missing` and an unknown
  tag becomes a new row, validated through the model's `clean()` first.
- **Admin ready.** Swap `admin.ModelAdmin` for `TagsInputAdmin` and every
  `ManyToManyField` on the model becomes a tag input. Tabular and stacked
  inlines are included.
- **Plain forms too.** `TagsInputField` is a `ModelMultipleChoiceField`, so it
  drops into any `forms.Form` or `ModelForm`.
- **Composite labels.** Build the tag text from several fields with a
  separator of your choice, and the input splits them back on save.
- **Fully typed and tested.** Ships `py.typed`, passes mypy, basedpyright and
  pyrefly in strict mode, and runs at 100% branch coverage across Django 5.2,
  6.0 and 6.1 on Python 3.10 to 3.14.

## Installation

```bash
pip install django-tags-input
# or
uv add django-tags-input
```

Python 3.10+ and Django 5.2+ are required. The widget bundles jQuery 3.2,
jQuery UI 1.12 and the tagsinput-revisited plugin, so no front-end build step
is needed.

## Quickstart

Three settings changes and one admin class get you the screenshot above.

**1. Add the app** to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'tags_input',
]
```

**2. Map the models you want to tag** in `TAGS_INPUT_MAPPINGS`. The key is
`app_label.ModelName`, the value says which field holds the tag text:

```python
TAGS_INPUT_MAPPINGS = {
    'blog.Tag': {
        'field': 'name',
        'create_missing': True,
    },
    'blog.Author': {
        'fields': ('first_name', 'last_name'),
        'separator': ' ',
        'ordering': ['last_name', 'first_name'],
        'filters': {'is_active': True},
    },
}
```

**3. Include the autocomplete URLs** in your root `urls.py`. The namespace
must be `tags_input`:

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path('tags_input/', include('tags_input.urls', namespace='tags_input')),
]
```

**4. Use it in the admin:**

```python
from django.contrib import admin

from tags_input import admin as tags_input_admin

from . import models


@admin.register(models.Post)
class PostAdmin(tags_input_admin.TagsInputAdmin):
    # Optional: restrict the tag widget to some ManyToMany fields. Without it
    # every ManyToManyField on the model becomes a tags input.
    tag_fields = ['tags', 'authors']
```

Open a `Post` in the admin and the `tags` and `authors` selects are now tag
boxes with autocomplete. Missing tags are created on save because the mapping
sets `create_missing`, while unknown authors are rejected with a validation
error.

## Outside the admin

`TagsInputField` works in any form. Pass it the queryset the tags come from
and render the form's media so the JavaScript and CSS load:

```python
from django import forms

from tags_input import fields

from . import models


class PostForm(forms.ModelForm):
    tags = fields.TagsInputField(
        models.Tag.objects.all(),
        create_missing=True,
        required=False,
    )

    class Meta:
        model = models.Post
        fields = ['title', 'tags']
```

```django
{{ form.media }}
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
</form>
```

<img src="https://raw.githubusercontent.com/WoLpH/django-tags-input/develop/docs/_static/form-demo.png" alt="A plain Django form rendering a tags input with autocomplete suggestions" width="700">

The widget ships its own jQuery and jQuery UI. If your page already loads
them, set `TAGS_INPUT_INCLUDE_JQUERY = False` to leave them out of the form
media.

## Tag order

The admin form mixin re-links the related objects in the order you typed
them, so the auto-created through table records that order. Read it back with
`utils.get_tags()`, which returns a queryset ordered the same way:

```python
from tags_input import utils

post = models.Post.objects.get(pk=1)
tags = utils.get_tags(post, 'tags')
[tag.name for tag in tags]
# ['B', 'A', 'C']
```

Plain `post.tags.all()` still returns whatever order the database picks. Use
`get_tags()` wherever the order matters.

## Mapping reference

Each entry in `TAGS_INPUT_MAPPINGS` accepts these keys:

| Key | Default | Meaning |
| --- | --- | --- |
| `field` | required (or `fields`) | The model field whose value is the tag text. |
| `fields` | required (or `field`) | Several fields joined into one label. |
| `separator` | `' - '` | Joins `fields` into a label and splits typed tags back into field values. |
| `create_missing` | `False` | Create objects for unknown tags instead of raising a validation error. |
| `queryset` | `Model.objects.all()` | A queryset, or a callable taking the mapping and returning one. Limits both autocomplete and validation. |
| `filters` | `{}` | Extra `filter()` kwargs applied to autocomplete suggestions. |
| `excludes` | `{}` | Extra `exclude()` kwargs applied to autocomplete suggestions. |
| `ordering` | the label fields | `order_by()` arguments for the suggestion list. |
| `autocomplete_queryset_filter` | `istartswith` match | Callable `(queryset, field, term)` returning the filtered queryset, for custom matching. |
| `join_func` | `utils.join_func` | Callable `(fields, separator, row)` returning `(pk, label)`. |
| `split_func` | `utils.split_func` | Callable `(fields, separator, label)` returning field values for a new object. |
| `filter_func` | `utils.filter_func` | Callable `(fields, separator, labels)` returning the lookup kwargs used to find typed tags. |

Tag lookups are case-insensitive, so `django` and `Django` resolve to the same
object.

The autocomplete endpoint lives at
`<prefix>/autocomplete/<app>/<model>/<field-names>/` and takes two query
parameters: `term` (the typed prefix) and `max_results` (default 10). It
answers with a JSON list of labels.

## Settings

| Setting | Default | Purpose |
| --- | --- | --- |
| `TAGS_INPUT_MAPPINGS` | `{}` | The mapping table described above. |
| `TAGS_INPUT_INCLUDE_JQUERY` | `True` | Include the bundled jQuery and jQuery UI in `TagsInputWidget.Media`. |
| `TAGS_INPUT_ADMIN_CSS` | bundled CSS | Override the CSS the admin widget loads. |
| `TAGS_INPUT_ADMIN_JS` | bundled JS | Override the JavaScript the admin widget loads. |

## JavaScript hooks

`TagsInputWidget` and `AdminTagsInputWidget` accept `on_add_tag`,
`on_remove_tag` and `on_change_tag`. Each is a JavaScript expression that is
inserted verbatim as the plugin callback:

```python
widget = widgets.TagsInputWidget(on_add_tag='function (tag) { console.log(tag); }')
```

## Running the example project

The repository ships a demo project with fixtures, which is also what the test
suite runs against:

```bash
git clone https://github.com/WoLpH/django-tags-input.git
cd django-tags-input
uv sync
uv run python example/manage.py migrate
uv run python example/manage.py migrate --database=other
uv run python example/manage.py loaddata example/fixtures.json
uv run python example/manage.py runserver
```

Open <http://localhost:8000/> for the plain form demo and
<http://localhost:8000/admin/> for the admin, and log in with `admin` /
`admin`. Some models in the example raise validation errors on purpose to show
how the widget behaves when saving fails.

## Documentation

Guides and the full API reference live at
**<https://django-tags-input.readthedocs.io/en/latest/>**.

## Links

- Documentation: <https://django-tags-input.readthedocs.io/en/latest/>
- Source: <https://github.com/WoLpH/django-tags-input>
- PyPI: <https://pypi.python.org/pypi/django-tags-input>
- Issues: <https://github.com/WoLpH/django-tags-input/issues>
- Changelog: <https://github.com/WoLpH/django-tags-input/blob/develop/CHANGELOG.md>
- Author's blog: <https://wol.ph/>

## Contributing

Contributions are welcome. The project keeps a 100% coverage bar and runs
Ruff, three type checkers and the full Django matrix in CI. See
[CONTRIBUTING.md](https://github.com/WoLpH/django-tags-input/blob/develop/CONTRIBUTING.md)
to get set up.

## Licence

BSD-3-Clause. See
[LICENSE](https://github.com/WoLpH/django-tags-input/blob/develop/LICENSE).
