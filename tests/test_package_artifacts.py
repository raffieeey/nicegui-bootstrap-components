"""Tests that the package ships the files its public contract promises."""

from __future__ import annotations

from pathlib import Path

import tomllib

from nicegui_bootstrap_components import __version__

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIR = REPO_ROOT / "src" / "nicegui_bootstrap_components"


def test_py_typed_marker_exists() -> None:
    marker = PACKAGE_DIR / "py.typed"
    assert marker.is_file(), (
        f"{marker} is missing; PEP 561 type information is not exported without it."
    )


def test_py_typed_marker_is_empty() -> None:
    assert (PACKAGE_DIR / "py.typed").stat().st_size == 0


def test_wheel_packages_include_source_directory() -> None:
    with (REPO_ROOT / "pyproject.toml").open("rb") as toml_file:
        pyproject = tomllib.load(toml_file)
    packages = pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
    assert "src/nicegui_bootstrap_components" in packages


def test_runtime_bundled_data_is_present() -> None:
    contract = PACKAGE_DIR / "contracts" / "dbc-2.0.4.json"
    assert contract.is_file()
    assert contract.stat().st_size > 0
    css_files = list((PACKAGE_DIR / "static").rglob("*.css"))
    assert len(css_files) > 0
    assert all(path.is_file() and path.stat().st_size > 0 for path in css_files)


def test_version_matches_pyproject() -> None:
    with (REPO_ROOT / "pyproject.toml").open("rb") as toml_file:
        pyproject = tomllib.load(toml_file)
    assert __version__ == pyproject["project"]["version"]
