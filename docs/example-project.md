# The example project

The repository ships a small Django project in `example/`. It is the demo,
and it is also what the test suite runs against.

## Running it

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

## What is inside

The `autocompletionexample` app has the models used by the tests:

- `Foo` is the simplest tag model, mapped with `create_missing`. Its
  `full_clean()` always raises, so creating a missing `Foo` shows how a
  validation error surfaces in the widget.
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
