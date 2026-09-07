from typing import Any, ClassVar

from django.db import models


class Router:
    TABLE_MAPPINGS: ClassVar[dict[str, str]] = {
        'autocompletionexample_extraspam': 'other',
        'autocompletionexample_fooextraspam': 'other',
    }

    def get_db(self, model: type[models.Model], **hints: Any) -> str:
        meta: Any = getattr(model, '_meta', None)
        db_table: str = str(getattr(meta, 'db_table', ''))
        return self.TABLE_MAPPINGS.get(db_table, 'default')

    def db_for_read(self, model: type[models.Model], **hints: Any) -> str:
        return self.get_db(model, **hints)

    def db_for_write(self, model: type[models.Model], **hints: Any) -> str:
        return self.get_db(model, **hints)

    def allow_migrate(self, *args: Any, **hints: Any) -> str:
        # Django 1.8, 1.9, 1.10 and 2.2 all have different behaviour... sigh
        model_name: str
        if 'model_name' in hints:
            model_name = str(hints['model_name'])
        elif 'model' in hints:
            model_name = str(hints['model']._meta.db_table)
        elif hasattr(args[1], '_meta'):
            model_name = str(args[1]._meta.db_table)
        else:
            model_name = str(args[1])

        return self.TABLE_MAPPINGS.get(model_name, 'default')

    def allow_relation(self, obj1: Any, obj2: Any, **hints: Any) -> bool:
        return True


__all__: list[str] = ['Router']
