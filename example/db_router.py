class Router(object):
    TABLE_MAPPINGS = {
        'autocompletionexample_extraspam': 'other',
        'autocompletionexample_fooextraspam': 'other',
    }

    def get_db(self, model, **hints):
        return self.TABLE_MAPPINGS.get(model._meta.db_table, 'default')

    db_for_read = db_for_write = get_db

    def allow_migrate(self, *args, **hints):
        # Django 1.8, 1.9, 1.10 and 2.2 all have different behaviour... sigh
        if 'model_name' in hints:
            model_name = hints['model_name']
        elif 'model' in hints:
            model_name = hints['model']._meta.db_table
        elif hasattr(args[1], '_meta'):
            model_name = args[1]._meta.db_table
        else:
            model_name = args[1]

        return self.TABLE_MAPPINGS.get(model_name, 'default')

    def allow_relation(self, obj1, obj2, **hints):
        return True
