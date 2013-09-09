
class Router(object):
    TABLE_MAPPINGS = {
        'autocompletionexample_extraspam': 'other',
        'autocompletionexample_fooextraspam': 'other',
    }

    def get_db(self, model, **hints):
        return self.TABLE_MAPPINGS.get(model._meta.db_table, 'default')

    db_for_read = db_for_write = get_db

    def allow_migrate(self, db, model):
        return self.TABLE_MAPPINGS.get(model._meta.db_table, 'default')

    def allow_relation(self, obj1, obj2, **hints):
        return True

