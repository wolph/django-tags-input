"""Native admin uses the package's ordered many-to-many widgets."""

from collections.abc import Sequence
from typing import ClassVar

from django.contrib import admin

from tags_input.admin import TagsInputAdmin

from .models import Article, Contact, Tag


@admin.register(Article)
class ArticleAdmin(TagsInputAdmin):
    """Use ordered tags input widgets for both relations."""

    tag_fields: ClassVar[Sequence[str] | set[str] | None] = [
        'tags',
        'contacts',
    ]


admin.site.register(Tag)
admin.site.register(Contact)
