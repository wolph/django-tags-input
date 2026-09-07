# Changelog

## Unreleased

### Breaking changes

- Django 5.2 LTS is now the minimum supported version. The suite runs against
  Django 5.2, 6.0 and 6.1 on Python 3.10 to 3.14, and Django 6.x itself
  requires Python 3.12 or newer.
- Python 3.9 and older are no longer supported.
- `TagsInputField.clean()` now returns the selected objects in the order the
  tags were entered instead of database order.
- The `on_add_tag`, `on_remove_tag` and `on_change_tag` arguments of
  `TagsInputWidget` are keyword-only. Positional use bound them to the wrong
  values when the admin widget was constructed through Django's
  `FilteredSelectMultiple`, which also dropped the widget `attrs`.

### Added

- Tag order is preserved. `TagsInputAdmin` and the new `TagsInputFormMixin`
  re-link the related objects in the entered order on save, the widget renders
  them in that order, and `utils.get_tags(instance, field_name)` reads the
  ordered tags back.
- `TagsInputMixin.get_form()` and `get_formset()` wrap the admin form with
  `TagsInputFormMixin` automatically, including for inlines.
- The widget accepts model instances, integer primary keys and numeric strings
  as initial values.
- `AdminTagsInputWidget` accepts the same `on_add_tag`, `on_remove_tag` and
  `on_change_tag` keyword arguments as `TagsInputWidget`.
- Full type annotations and a `py.typed` marker. The package is checked with
  mypy, basedpyright and pyrefly in strict mode.

### Changed

- Packaging moved to `pyproject.toml` with the `uv_build` backend. `setup.py`,
  `setup.cfg`, `MANIFEST.in` and the requirements files are gone. The version
  is read from the installed metadata at runtime.
- The wheel ships only the minified assets the widgets reference. The vendored
  jQuery UI and tagsinput-revisited source trees stay in the repository.
- Development tooling: Ruff for linting and formatting, codespell, lefthook
  git hooks, and a tox matrix driven by tox-uv that CI runs unchanged.
- CI is split into test, lint, type-check, spelling, docs and coverage jobs,
  with CodeQL scanning and PyPI Trusted Publishing on tags. The coverage gate
  is 100% branch coverage over the combined matrix.
- The README was rewritten in Markdown with screenshots, a mapping reference
  and a settings reference. The Sphinx documentation uses the furo theme with
  guides for the admin, plain forms, configuration and tag ordering.
- The example project no longer tracks its SQLite databases. Run the
  migrations and load `example/fixtures.json` to recreate them.

## 6.0.0 - 2023-03-01

- Updated to support newer versions of Django and Python. Tested with Django
  4.2 and Python 3.11.

Older releases are listed on the
[GitHub releases page](https://github.com/WoLpH/django-tags-input/releases).
