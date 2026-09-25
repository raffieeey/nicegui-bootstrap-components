# Releasing

Maintainer guide for publishing nicegui-bootstrap-components.

## Version bump

Set the same version in:

- `pyproject.toml` (`[project] version`)
- the package `__version__` in `src/nicegui_bootstrap_components/__init__.py`

Move the notes in `CHANGELOG.md` from `## [Unreleased]` into a dated
`## [X.Y.Z] - YYYY-MM-DD` section. Leave an empty `## [Unreleased]` heading
above it.

## Pre-release check

From the repository root:

```bash
python scripts/release_check.py
```

`--skip-build` skips the wheel build and smoke test. `--skip-docs` skips
`mkdocs build --strict`. Every step must be PASS (or an intentional SKIP)
before tagging.

## Parity checklist

Do not tag until all of these are green:

- ruff check and ruff format
- mypy
- pytest (L1 and L2)
- manifest check
- mkdocs build
- example import smoke

Pull requests and pushes to `main` run the `CI` workflow (ruff, mypy, pytest,
and `mkdocs build --strict`).

## Wheel release-candidate test (offline)

Build a wheel and install it in an empty virtualenv that does not include the
source tree:

```bash
python -m build --wheel
python -m venv /tmp/nbc-rc
/tmp/nbc-rc/bin/pip install dist/nicegui_bootstrap_components-*.whl nicegui
```

Disable the network and confirm `import nicegui_bootstrap_components` still
works with cached/offline assets. For a release candidate, run the full L3
suite against that installed wheel.

## PyPI Trusted Publishing

Do not store PyPI tokens or other publish secrets in the repository. On PyPI,
register a trusted publisher for this GitHub repository using:

- Workflow name: `publish.yml` (PyPI matches the workflow *file name*; the
  workflow's display name is `Publish`)
- Environment name: `pypi`

The project does not exist on PyPI yet, so the first release uses a **pending**
publisher: register it under Account → Publishing (not a project's settings),
fill in the same four values plus the project name
`nicegui-bootstrap-components`, and it converts to a normal publisher on first
use. A pending publisher reserves nothing: publish before anyone else claims
the name.

The publish workflow should request `id-token: write` and use the `pypi`
GitHub Environment.

## Tag and GitHub Release

1. Commit the version bump and changelog on `main`.
2. Create an annotated tag `vX.Y.Z` and push it.
3. Open a GitHub Release for that tag and paste the changelog section.
4. Publish the sdist and wheel to PyPI through Trusted Publishing.

## Post-release docs

Build docs with `mkdocs build --strict` and publish them for the tagged
version. If the documentation site is versioned, add this release to the
version list and point the default/latest alias at it.
