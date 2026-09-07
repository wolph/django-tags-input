# Run the examples locally

The `showcase` app supplies the same forms used in the browser example.
Run it locally to inspect validation, saved relations and the Django admin:

```bash
git clone https://github.com/WoLpH/django-tags-input.git
cd django-tags-input
uv sync --all-groups
export DJANGO_SETTINGS_MODULE=showcase.settings
uv run python -m django migrate --run-syncdb
uv run python -m django seed_showcase
uv run python -m django createsuperuser
uv run python -m django runserver
```

Open <http://localhost:8000/> for the forms and
<http://localhost:8000/admin/> for the admin. The seed command creates tags and
contact names covering A-Z, including Django, Python, PostgreSQL and Redis,
and one article per example. Every initial has an autocomplete suggestion.
Use your newly created account to log in to the admin.

The standalone SQLite file is `showcase/showcase.sqlite3`. Set
`SHOWCASE_DATABASE` to use another file. These development settings bind to
localhost by default through `runserver` and are intended for local examples.

## The regression test project

The repository ships a small Django project in `example/`. It contains older fixtures and the deliberately invalid models used by the
regression tests.

### Running the regression project

```bash
git clone https://github.com/WoLpH/django-tags-input.git
cd django-tags-input
uv sync
uv run python example/manage.py migrate
uv run python example/manage.py migrate --database=other
uv run python example/manage.py loaddata example/fixtures.json
uv run python example/manage.py runserver
```

Open <http://localhost:8000/> for a plain form using
{class}`~tags_input.fields.TagsInputField`, and <http://localhost:8000/admin/>
for the admin. Log in with `admin` / `admin`.

The second `migrate` is needed because the example routes two models to a
second SQLite database through `example/db_router.py`, to prove the widget
does not care which database the tagged model lives in.

### What is inside

The `autocompletionexample` app has the models used by the tests:

- `Foo` is the simplest tag model, mapped with `create_missing`. Its
  `full_clean()` deliberately raises. Tag creation calls `clean()` instead,
  so that separate method is not part of the tag field's creation path.
- `Spam` has a `ManyToManyField` to `Foo`, and its mapping uses a callable
  `queryset`. Its `clean()` also raises on purpose.
- `Egg` maps two fields, `name` and `name2`, into one composite label.
- `ExtraSpam` links to `Foo` through a custom `through` model and lives in the
  second database.

The `demo` app has a wider set of models named after what they exercise:
`SimpleName`, `DoubleName`, `ManyToManyToSimpleName`, `ManyToManyThrough`,
`InlineModel` and friends. Its admin registers every model with
{class}`~tags_input.admin.TagsInputAdmin`, and `SimpleName` has a stacked
inline that shows the inline classes at work.

The deliberately broken models are there to test error paths. If a save in
the demo fails with `Expected testing error`, that is the model doing its job.
