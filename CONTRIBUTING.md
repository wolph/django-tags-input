# Contributing to django-tags-input

Bug reports, code and documentation contributions are welcome. Using the
development version and reporting what breaks helps too.

## Reporting bugs

Please include:

- the Python and Django versions
- the django-tags-input version
- the relevant `TAGS_INPUT_MAPPINGS` entry and the model it points at
- a minimal reproducible example, if possible

## Contributing code and docs

Browse the [existing issues](https://github.com/WoLpH/django-tags-input/issues)
before starting on a feature or a fix. If your change alters behaviour or the
public interface, open an issue first so the design can be discussed.

When fixing a bug, start with a test that reproduces it. Pull requests need
tests and documentation for the change. The project holds a strict 100% branch
coverage bar and every type checker must stay clean.

### Development environment

```bash
git clone git@github.com:<YOU>/django-tags-input.git
cd django-tags-input
uv sync --all-groups
uv run lefthook install
```

`uv sync --all-groups` installs the package in editable mode together with the
test, docs and dev tooling. `lefthook install` sets up the git hooks: Ruff and
codespell run on commit, Ruff, mypy and a quick test run on push.

### Running the checks

The quick loop during development:

```bash
uv run pytest                 # tests with the 100% coverage gate
uv run ruff check . && uv run ruff format --check .
uv run mypy && uv run basedpyright && uv run pyrefly check
uv run codespell
uv run sphinx-build -W -b html docs docs/_build/html
```

The full matrix is what CI runs. tox drives it and provisions any missing
Python through uv:

```bash
uv run --group tox tox -p auto   # everything: Django x Python matrix + checks
uv run --group tox tox -m check  # static checks only
uv run --group tox tox -m test   # the Django x Python matrix only
uv run --group tox tox -e py312-django61,lint
```

### The example project

The test suite runs against the `example` project, which doubles as a demo:

```bash
uv run python example/manage.py migrate
uv run python example/manage.py migrate --database=other
uv run python example/manage.py loaddata example/fixtures.json
uv run python example/manage.py runserver
```

Log in to <http://localhost:8000/admin/> with `admin` / `admin`.
