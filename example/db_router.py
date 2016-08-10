
class Router(object):
    TABLE_MAPPINGS = {
        'autocompletionexample_extraspam': 'other',
        'autocompletionexample_fooextraspam': 'other',
    }

    def get_db(self, model, **hints):
        return self.TABLE_MAPPINGS.get(model._meta.db_table, 'default')

    db_for_read = db_for_write = get_db

    def allow_migrate(self, *args, **hints):
        if 'model_name' in hints:
            model_name = hints['model_name']
        else:
            db, model = args
            model_name = model._meta.db_table

        return self.TABLE_MAPPINGS.get(model_name, 'default')

    def allow_relation(self, obj1, obj2, **hints):
        return True

