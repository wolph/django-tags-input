# Django Tags Input

Ordered tags with autocomplete for Django forms and the admin.
Use an existing model for labels, allow new objects where appropriate, and
keep the selection order through form saves and reloads.

[![PyPI](https://img.shields.io/pypi/v/django-tags-input.svg)](https://pypi.org/project/django-tags-input/)
[![CI](https://github.com/WoLpH/django-tags-input/actions/workflows/ci.yml/badge.svg)](https://github.com/WoLpH/django-tags-input/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/django-tags-input.svg)](https://pypi.org/project/django-tags-input/)

[Try the forms](https://django-tags-input.readthedocs.io/en/latest/playground.html)
| [Documentation](https://django-tags-input.readthedocs.io/en/latest/)
| [Source](https://github.com/WoLpH/django-tags-input)

<img src="https://raw.githubusercontent.com/WoLpH/django-tags-input/develop/docs/_static/admin-autocomplete.png" alt="Django admin tags input with selected tags and autocomplete suggestions" width="900">

The browser example runs real Django forms and SQLite on your device.
It supports tag creation, existing choices and composite contact labels.
Saved tags persist across reloads. No public Django server receives them.

## Install

```bash
uv add django-tags-input
```

Python 3.10+ and Django 5.2+ are required. Django 6.x requires Python 3.12+.
The package includes the widget's JavaScript and CSS, so using it does not
require Node.js or a frontend build.

## Add tags to the admin

In an existing Django app named `blog`, give posts a relation to tag objects:

```python
from __future__ import annotations

from django.db import models


class Tag(models.Model):
    name: models.CharField[str, str] = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    title: models.CharField[str, str] = models.CharField(max_length=200)
    tags: models.ManyToManyField[Tag, Tag] = models.ManyToManyField(
        Tag, blank=True,
    )
```

Each tag is an ordinary model row. The post stores the relationship through
Django's automatically created join table.

Add the widget app and its mapping to your settings:

```python
INSTALLED_APPS += ['tags_input']

TAGS_INPUT_MAPPINGS: dict[str, dict[str, object]] = {
    'blog.Tag': {'field': 'name', 'create_missing': True},
}
```

The key identifies the model. `field` supplies the visible label, and
`create_missing` permits a new tag when no existing label matches.
Keep it disabled when users must choose existing objects.

Include the autocomplete route in the project's `urls.py`:

```python
from django.urls import include, path

urlpatterns += [
    path('tags-input/', include('tags_input.urls', namespace='tags_input')),
]
```

The namespace must be `tags_input`. One route serves the mapped models.

Register the post with the package's admin class:

```python
from typing import ClassVar

from django.contrib import admin
from tags_input.admin import TagsInputAdmin

from .models import Post


@admin.register(Post)
class PostAdmin(TagsInputAdmin):
    tag_fields: ClassVar[list[str]] = ['tags']
```

Create the tables and open a post in the admin:

```bash
uv run python manage.py makemigrations blog
uv run python manage.py migrate
uv run python manage.py runserver
```

The `tags` field now offers autocomplete. Saving a new label creates a tag
object after calling its `clean()` method. Existing labels become relations
in the order entered.

> [!NOTE]
> The autocomplete endpoint does not check permissions. For private labels,
> restrict access in your own view or middleware and pass the permitted
> queryset to the form field. Suggestion filters alone do not restrict saves.

## Use a form outside the admin

Use both the field and the form mixin when the order must survive saves:

```python
from __future__ import annotations

from typing import ClassVar

from django import forms
from tags_input.admin import TagsInputFormMixin
from tags_input.fields import TagsInputField

from .models import Post, Tag


class PostForm(TagsInputFormMixin, forms.ModelForm):
    tags: TagsInputField = TagsInputField(Tag.objects.all(), required=False)

    class Meta:
        model: type[Post] = Post
        fields: ClassVar[list[str]] = ['title', 'tags']
```

`TagsInputField` validates labels against its queryset. The mixin saves the
related objects in that order. Render the form media alongside the form:

```django
{{ form.media }}
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
</form>
```

The media loads the bundled jQuery, jQuery UI and tagsinput plugin. If your
page already loads compatible jQuery and jQuery UI, set
`TAGS_INPUT_INCLUDE_JQUERY = False`.

<img src="https://raw.githubusercontent.com/WoLpH/django-tags-input/develop/docs/_static/form-demo.png" alt="A Django form with autocomplete and selected tags" width="800">

Read the saved order with `tags_input.utils.get_tags(post, 'tags')`.
`post.tags.all()` uses the model or database ordering instead.

## Guides and development

- [Configuration](https://django-tags-input.readthedocs.io/en/latest/configuration.html): mappings, callbacks and matching rules.
- [Admin and inlines](https://django-tags-input.readthedocs.io/en/latest/admin.html): choosing fields and handling relationship signals.
- [Order](https://django-tags-input.readthedocs.io/en/latest/ordering.html): how the join table records selections and where that approach applies.
- [Local examples](https://django-tags-input.readthedocs.io/en/latest/example-project.html): run the same forms and inspect the admin.
- [Contributing](https://github.com/WoLpH/django-tags-input/blob/develop/CONTRIBUTING.md): uv, strict typing, linting, documentation and coverage checks.

The test matrix covers Python 3.10-3.14 with compatible Django 5.2, 6.0 and
6.1 releases. The project requires 100% statement and branch coverage and
checks types with mypy, basedpyright and pyrefly.
