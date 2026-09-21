# Contributing

Contributions are welcome. Bug reports, fixes, documentation, and examples
all help. Changes should keep the native (`bs`) and compat (`dbc`) surfaces
aligned with the documented Bootstrap 5.3 contract.

## Development setup

Clone this repository and change into the project root. Install the package
in editable mode with development extras:

```bash
pip install -e ".[dev]"
```

Python 3.10 or later is required.

The browser suite needs Chromium:

```bash
python -m playwright install chromium
```

A virtual environment is recommended so the editable install and Playwright
browsers stay isolated from other projects.

## Running the tests

The default suite deselects browser and visual tests via markers:

```bash
pytest
```

Playwright L3 suite:

```bash
pytest -m browser
```

Screenshot-matrix tests:

```bash
pytest tests/visual --visual
```

Visual baselines are compared with a tolerance for cross-platform font
rasterization. They are not pixel-exact.

## Code quality

Run these before opening a pull request:

```bash
ruff check .
ruff format --check . --exclude "*.md"
mypy
```

`mypy` is configured for `src/`. Typed public APIs and lint-clean modules
are required.

CI runs all three of those checks plus `mkdocs build --strict`.

## Docs

Preview the site locally:

```bash
mkdocs serve
```

Component pages live in `docs_site/`. `mkdocs build --strict` must pass;
warnings fail the build.

Examples follow a same-source rule: the file that runs is the file shown in
the docs. Do not duplicate example bodies in Markdown.

## Pull requests

Keep pull requests small and focused. Describe the change and how you
tested it.

- Add or update tests for behaviour changes.
- Do not edit generated files.
- Keep documentation prose original, concise, and specific to this library.

CI runs the `checks`, `docs`, and `browser` jobs on every pull request.

## Reporting issues

Include a minimal reproducible example, the NiceGUI and package versions,
and what you expected versus what happened. When the issue is
component-specific, say which surface you used (`bs` or `dbc`).

## Code of conduct and license

This project follows `CODE_OF_CONDUCT.md`. The library is released under
the MIT license; see `LICENSE`.
