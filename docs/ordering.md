# Tag order

Most tagging widgets treat a relation as a set. This one treats it as a list.
Enter `B, A, C` and the widget shows `B, A, C` the next time the form loads,
and {func}`~tags_input.utils.get_tags` returns the objects in that order.

## How the order is stored

Django's auto-created through table has its own auto-incrementing primary
key, and rows are inserted in the order `add()` is called. The form mixin
uses that: on save it clears the relation and adds the objects back one by
one in the order they were typed. The through table's primary key order is
now the tag order.

Nothing else changes in your schema. There is no extra ordering column and no
migration.

## Reading the order back

`instance.tags.all()` returns whatever order the database picks, which is
often but not reliably the insertion order. Use
{func}`~tags_input.utils.get_tags` wherever the order matters:

```python
from tags_input import utils

post = models.Post.objects.get(pk=1)
tags = utils.get_tags(post, 'tags')
[tag.name for tag in tags]
# ['B', 'A', 'C']
```

`get_tags()` returns a queryset ordered with a `Case`/`When` expression built
from the through rows, so you can chain further `filter()` calls on it. It
returns an empty list when the attribute is not a many-to-many manager, and an
empty queryset when the relation has no rows.

## Limits

The approach relies on the auto-created through table. Relations with a
custom `through` model keep their own semantics and are skipped by both the
form mixin and the admin, the same way Django's admin skips them.

Re-saving the relation on every form save also means the through rows get new
primary keys each time. If something else stores those through ids, it will
break. In practice nothing should.
