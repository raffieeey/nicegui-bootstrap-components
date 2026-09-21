from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from nicegui_bootstrap_components import icons, themes
from nicegui_bootstrap_components.assets import _reset_setup, setup
from nicegui_bootstrap_components.theme import _resolve_theme

ROOT = Path(__file__).resolve().parents[1]
STYLE_DIST = ROOT / "styles" / "dist"

THEME_NAMES = (
    "bootstrap",
    "grid",
    "cerulean",
    "cosmo",
    "cyborg",
    "darkly",
    "flatly",
    "journal",
    "litera",
    "lumen",
    "lux",
    "materia",
    "minty",
    "morph",
    "pulse",
    "quartz",
    "sandstone",
    "simplex",
    "sketchy",
    "slate",
    "solar",
    "spacelab",
    "superhero",
    "united",
    "vapor",
    "yeti",
    "zephyr",
)


@pytest.fixture(autouse=True)
def _isolated_setup() -> Any:
    _reset_setup()
    yield
    _reset_setup()


def test_catalogue_exports_and_resolves() -> None:
    assert set(THEME_NAMES).issubset({getattr(themes, name.upper()).name for name in THEME_NAMES})
    assert set(name.upper() for name in THEME_NAMES).issubset(set(themes.__all__))
    for name in THEME_NAMES:
        constant = getattr(themes, name.upper())
        assert _resolve_theme(constant) is constant
        assert _resolve_theme(name) is constant


@pytest.mark.parametrize("name", THEME_NAMES)
def test_catalogue_bundled_files_exist(name: str) -> None:
    theme = getattr(themes, name.upper())
    path = STYLE_DIST / f"{theme.bundled}.css"
    if not path.is_file():
        pytest.skip("style build is absent")
    assert path.is_file()
    assert (STYLE_DIST / f"{theme.bundled}-unscoped.css").is_file()


def test_unknown_theme_lists_valid_names() -> None:
    with pytest.raises(ValueError, match="valid names:.*bootstrap.*grid"):
        _resolve_theme("not-a-theme")


def test_icon_constants_are_pinned() -> None:
    assert "bootstrap-icons@1.11.3" in icons.BOOTSTRAP.cdn
    assert "fontawesome-free@6.7.2" in icons.FONT_AWESOME.cdn
    assert icons.BOOTSTRAP.bundled == "ngbs-icons-bootstrap"
    assert icons.FONT_AWESOME.bundled == "ngbs-icons-fontawesome"


def test_setup_injects_requested_icon_stylesheet(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import assets

    imports: list[str] = []
    monkeypatch.setattr(assets, "add_head_html", lambda code, **_kwargs: imports.append(code))
    monkeypatch.setattr(assets, "add_static_files", lambda *_args, **_kwargs: None)
    setup(icons="bootstrap")
    assert any("ngbs-icons-bootstrap.css" in value for value in imports)


def test_setup_without_icons_does_not_inject_icon_stylesheet(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nicegui_bootstrap_components import assets

    imports: list[str] = []
    monkeypatch.setattr(assets, "add_head_html", lambda code, **_kwargs: imports.append(code))
    monkeypatch.setattr(assets, "add_static_files", lambda *_args, **_kwargs: None)
    setup(icons=None)
    assert not any("ngbs-icons-" in value for value in imports)
