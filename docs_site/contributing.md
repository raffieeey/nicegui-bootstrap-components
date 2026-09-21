# Contributing

Contributions that keep the native and compat surfaces aligned with the
documented Bootstrap 5.3 contract are welcome.

## Development setup

Install the package in editable mode with development extras:

```bash
pip install -e .[dev]
```

## Running tests

```bash
pytest
```

Visual and accessibility baselines, when present:

```bash
pytest --visual
```

## Style gates

Run `ruff` and `mypy` before opening a pull request. Typed public APIs and
lint-clean modules are required.

## Documentation

```bash
mkdocs serve
```

Examples follow a same-source rule: the file that runs is the file shown in
the docs. Do not duplicate example bodies in Markdown.

## Pull request expectations

- Add or update tests for behaviour changes.
- Do not edit generated files.
- Keep documentation prose original, concise, and specific to this library.
