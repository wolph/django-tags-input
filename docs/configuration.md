# Configuration

All configuration lives in Django settings. `TAGS_INPUT_MAPPINGS` is required,
the rest have sensible defaults.

## Mappings

Each entry in `TAGS_INPUT_MAPPINGS` is keyed by `app_label.ModelName` and
accepts these keys:

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
| `autocomplete_queryset_filter` | `istartswith` match | Callable `(queryset, field, term)` returning the filtered queryset. |
| `join_func` | {func}`~tags_input.utils.join_func` | Callable `(fields, separator, row)` returning `(pk, label)`. |
| `split_func` | {func}`~tags_input.utils.split_func` | Callable `(fields, separator, label)` returning the field values for a new object. |
| `filter_func` | {func}`~tags_input.utils.filter_func` | Callable `(fields, separator, labels)` returning the lookup kwargs used to find typed tags. |

A mapping without `field` or `fields` raises
{class}`~tags_input.exceptions.ConfigurationError` the first time it is used.
Asking for a model that has no mapping raises
{class}`~tags_input.exceptions.MappingUndefined`.

### Single field labels

The simplest mapping names one field. Tags are matched case-insensitively, so
`django` and `Django` resolve to the same object:

```python
TAGS_INPUT_MAPPINGS = {
    'blog.Tag': {'field': 'name', 'create_missing': True},
}
```

### Composite labels

With `fields` the label is the field values joined by `separator`. On save
the label is split on the same separator, so a new object created through
`create_missing` gets each part stored in the right field:

```python
TAGS_INPUT_MAPPINGS = {
    'crm.Contact': {
        'fields': ('first_name', 'last_name'),
        'separator': ' ',
        'create_missing': True,
    },
}
```

Typing `Ada Lovelace` creates `Contact(first_name='Ada', last_name='Lovelace')`
when no such contact exists. The split uses `str.split(separator, len(fields))`,
so a label with more separators than fields keeps the remainder in the last
field.

### Restricting the choices

`queryset`, `filters` and `excludes` narrow what the widget offers and
accepts. `queryset` may be a callable, which is handy when the queryset
depends on something that is not available at import time:

```python
def active_tags(mapping):
    from blog.models import Tag

    return Tag.objects.filter(is_active=True)


TAGS_INPUT_MAPPINGS = {
    'blog.Tag': {
        'field': 'name',
        'queryset': active_tags,
        'excludes': {'name__startswith': 'internal-'},
        'ordering': ['-usage_count', 'name'],
    },
}
```

`filters`, `excludes` and `ordering` only shape the autocomplete suggestions.
`queryset` also limits which objects validate on save.

### Custom matching

The default suggestion filter is `field__istartswith=term`. Replace it to
match anywhere in the label, or to search a different column:

```python
def contains(queryset, field, term):
    return queryset.filter(**{f'{field}__icontains': term})


TAGS_INPUT_MAPPINGS = {
    'blog.Tag': {
        'field': 'name',
        'autocomplete_queryset_filter': contains,
    },
}
```

## The autocomplete endpoint

`tags_input.urls` exposes one view:

```text
<prefix>/autocomplete/<app>/<model>/<field-names>/
```

`field-names` is the mapping's label fields joined by `-`. The view accepts
two query parameters, `term` for the typed prefix and `max_results` for the
number of suggestions (default 10), and answers with a JSON list of labels:

```text
GET /tags_input/autocomplete/blog/Tag/name/?term=dj&max_results=5
["django", "django-admin", "djangocon"]
```

The view respects the mapping's `queryset`, `filters`, `excludes` and
`ordering`. It does not check permissions, so if the labels are sensitive,
wrap `tags_input.views.autocomplete` in your own view or middleware.

## Settings

| Setting | Default | Purpose |
| --- | --- | --- |
| `TAGS_INPUT_MAPPINGS` | `{}` | The mapping table described above. |
| `TAGS_INPUT_INCLUDE_JQUERY` | `True` | Include the bundled jQuery and jQuery UI in `TagsInputWidget.Media`. Set it to `False` when your pages already load them. |
| `TAGS_INPUT_ADMIN_CSS` | bundled CSS | Override the CSS dict the admin widget loads. |
| `TAGS_INPUT_ADMIN_JS` | bundled JS | Override the JavaScript tuple the admin widget loads. |

The admin widget always loads its own jQuery because the Django admin only
exposes `django.jQuery`, not the global `jQuery` the plugin expects. Point
`TAGS_INPUT_ADMIN_JS` at your own copies if you need different versions.
