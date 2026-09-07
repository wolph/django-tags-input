# Getting started

## Installation

```bash
pip install django-tags-input
# or
uv add django-tags-input
```

Python 3.10+ and Django 5.2+ are required. Django 6.x needs Python 3.12 or
newer, which is Django's own floor rather than ours. The widget bundles jQuery
3.2, jQuery UI 1.12 and the tagsinput-revisited plugin, so there is no
front-end build step.

## Setup

Three settings changes and one admin class are all it takes.

### 1. Add the app

```python
INSTALLED_APPS = [
    # ...
    'tags_input',
]
```

### 2. Map the models you want to tag

`TAGS_INPUT_MAPPINGS` tells the package which models can be tagged and which
field holds the tag text. The key is `app_label.ModelName`:

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

The `Tag` mapping creates unknown tags on save. The `Author` mapping builds
each label from two fields, only suggests active authors, and rejects names
that do not match an existing author. Every key is described in
{doc}`configuration`.

### 3. Include the autocomplete URLs

The widget fetches suggestions from a view shipped with the package. Include
it once in your root `urls.py`. The namespace has to be `tags_input`, because
the widget reverses `tags_input:autocomplete`:

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path('tags_input/', include('tags_input.urls', namespace='tags_input')),
]
```

### 4. Use it in the admin

```python
from django.contrib import admin

from tags_input import admin as tags_input_admin

from . import models


@admin.register(models.Post)
class PostAdmin(tags_input_admin.TagsInputAdmin):
    tag_fields = ['tags', 'authors']
```

Open a `Post` in the admin and the `tags` and `authors` selects are tag boxes
with autocomplete. Leave `tag_fields` out to convert every `ManyToManyField`
on the model. See {doc}`admin` for inlines and the form mixin, and
{doc}`forms` for using the field outside the admin.

## What happens on save

The widget posts a comma separated string of labels. `TagsInputField.clean()`
looks the labels up case-insensitively, creates missing objects when the
mapping allows it, validates the primary keys through Django's
`ModelMultipleChoiceField`, and returns a queryset ordered the way the tags
were typed. The admin form mixin then links the objects in that order so the
order survives a round trip. {doc}`ordering` has the details.
