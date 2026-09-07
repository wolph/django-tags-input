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
uv run python tools/check_types.py mypy
uv run python tools/check_types.py pyright
uv run python tools/check_types.py pyrefly
uv run codespell
uv run python tools/build_docs.py
```

The full matrix is what CI runs. tox drives it and provisions any missing
Python through uv:

```bash
uv run --group tox tox -p auto   # everything: Django x Python matrix + checks
uv run --group tox tox -m check  # static checks only
uv run --group tox tox -m test   # the Django x Python matrix only
uv run --group tox tox -e py312-django61,lint
```

The documentation build requires Python 3.11+ and Node.js 24. It compiles the strict
TypeScript browser example and stages checksum-verified Python wheels.
The documentation and its browser package come from the same checkout.

Run the browser checks after building the documentation:

```bash
cd playground
npm ci
npm run check
npm exec playwright install chromium firefox webkit
npm test
```

These tests run actual Django in Pyodide, including storage and reset checks.
The `typing310` tox environment checks the oldest supported Python with
compatible Django stubs. Default type-check environments use newer stubs.

### The example project

The test suite runs against the `example` project, which doubles as a demo:

```bash
uv run python example/manage.py migrate
uv run python example/manage.py migrate --database=other
uv run python example/manage.py loaddata example/fixtures.json
uv run python example/manage.py runserver
```

Log in to <http://localhost:8000/admin/> with `admin` / `admin`.

### Capturing the documentation examples

Build the docs and serve the output on port 8779, then run the capture script
in another terminal:

```bash
uv run python tools/build_docs.py
uv run python -m http.server 8779 --bind 127.0.0.1 --directory docs/_build/html
# In another terminal:
node tools/capture_docs.mts
```

The script starts a fresh browser, uses the real form and saves screenshots
and a WebM recording under `docs/_static/`. Responsive review captures go to
`docs/_build/visual/`. The native admin screenshots use the seeded showcase
on localhost. The inline screenshot uses the regression project's fixtures.
