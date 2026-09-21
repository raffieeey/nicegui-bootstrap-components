"""Unit tests for the theme constants, setup() options, and ThemeController."""

from __future__ import annotations

from typing import Any

import pytest

from nicegui_bootstrap_components import themes
from nicegui_bootstrap_components.assets import StyleMode, _reset_setup, setup
from nicegui_bootstrap_components.theme import (
    ThemeController,
    _normalize_mode,
    _resolve_theme,
    ensure_theme_bound,
)


@pytest.fixture(autouse=True)
def _isolated_manager() -> Any:
    _reset_setup()
    yield
    _reset_setup()


class _FakeClient:
    """Minimal client stand-in: store bucket plus the two host hooks."""

    def __init__(self) -> None:
        self.extras: dict[str, Any] = {}
        self.scripts: list[str] = []

    def run_javascript(self, code: str) -> None:
        self.scripts.append(code)


def _patch_host(
    monkeypatch: pytest.MonkeyPatch,
    calls: list[tuple[str, str]],
    targets: list[Any] | None = None,
) -> None:
    from nicegui_bootstrap_components import theme as theme_module

    def fake_add_head_html(
        code: str,
        *,
        shared: bool = True,
        client: Any | None = None,
    ) -> None:
        calls.append(("head", code))
        if targets is not None:
            targets.append(client)

    def fake_run_javascript(code: str, *, client: Any | None = None) -> None:
        calls.append(("js", code))
        if targets is not None:
            targets.append(client)

    monkeypatch.setattr(theme_module, "add_head_html", fake_add_head_html)
    monkeypatch.setattr(theme_module, "run_javascript", fake_run_javascript)


# -- constants ---------------------------------------------------------


def test_theme_constants_are_pinned() -> None:
    for theme in (themes.BOOTSTRAP, themes.FLATLY, themes.DARKLY):
        assert "5.3.8" in theme.cdn
        assert theme.bundled.startswith("ngbs-")
        assert theme.name in theme.cdn


def test_resolve_theme_accepts_objects_names_and_urls() -> None:
    assert _resolve_theme(themes.FLATLY) is themes.FLATLY
    assert _resolve_theme("flatly") is themes.FLATLY
    assert _resolve_theme("darkly") is themes.DARKLY
    custom = _resolve_theme("https://example.test/theme.css")
    assert custom.cdn == "https://example.test/theme.css"
    assert custom.bundled == ""


@pytest.mark.parametrize("value", ['https://example.test/"}theme.css', "javascript:alert(1)"])
def test_resolve_theme_rejects_css_injection_strings(value: str) -> None:
    with pytest.raises(ValueError):
        _resolve_theme(value)


def test_normalize_mode_validates() -> None:
    assert _normalize_mode("LIGHT") == "light"
    assert _normalize_mode("dark") == "dark"
    assert _normalize_mode("auto") == "auto"
    with pytest.raises(ValueError):
        _normalize_mode("sepia")


# -- setup() -----------------------------------------------------------


def test_setup_cdn_requires_unscoped(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []
    _patch_host(monkeypatch, calls)
    with pytest.raises(ValueError):
        setup(mode=StyleMode.MIXED, cdn=True)


def test_setup_unscoped_cdn_injects_import(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import assets

    calls: list[tuple[str, str]] = []
    _patch_host(monkeypatch, calls)
    imports: list[str] = []

    def capture_head(code: str, **_kwargs: Any) -> None:
        imports.append(code)

    monkeypatch.setattr(assets, "add_head_html", capture_head)
    monkeypatch.setattr(assets, "add_static_files", lambda *_a, **_k: None)
    setup(mode=StyleMode.UNSCOPED, cdn=True, theme=themes.FLATLY)
    from nicegui_bootstrap_components.assets import get_asset_manager

    manager = get_asset_manager()
    assert manager is not None
    assert manager.theme is themes.FLATLY
    assert manager.cdn is True
    assert len(imports) == 1
    assert "bootswatch@5.3.8" in imports[0]
    assert "ngbs-flatly" not in imports[0]


def test_setup_rejects_invalid_color_mode() -> None:
    with pytest.raises(ValueError, match=r"light\|dark\|auto"):
        setup(color_mode="grey")


def test_setup_rejects_later_argument_conflicts(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import assets

    monkeypatch.setattr(assets, "add_head_html", lambda *_a, **_k: None)
    monkeypatch.setattr(assets, "add_static_files", lambda *_a, **_k: None)
    setup(mode=StyleMode.MIXED)
    with pytest.raises(ValueError, match="color_mode"):
        setup(mode=StyleMode.MIXED, color_mode="dark")
    with pytest.raises(ValueError, match="theme"):
        setup(mode=StyleMode.MIXED, theme=themes.DARKLY)


def test_missing_bundled_theme_is_loud(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import assets

    monkeypatch.setattr(assets, "add_head_html", lambda *_a, **_k: None)
    monkeypatch.setattr(assets, "add_static_files", lambda *_a, **_k: None)
    missing = themes.Theme(
        name="missing",
        cdn="https://example.test/missing.css",
        bundled="ngbs-missing",
    )
    with pytest.raises(FileNotFoundError, match="dist/ngbs-missing.css"):
        setup(theme=missing)


def test_bundled_url_rejects_missing_theme_build(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import assets

    monkeypatch.setattr(assets, "add_static_files", lambda *_a, **_k: None)
    missing = themes.Theme(
        name="missing",
        cdn="https://example.test/missing.css",
        bundled="ngbs-missing",
    )
    manager = assets.AssetManager(StyleMode.MIXED, theme=missing)
    with pytest.raises(FileNotFoundError, match="dist/ngbs-missing.css"):
        manager.bundled_url(missing)
    manager.close()


# -- ThemeController ---------------------------------------------------


def test_for_client_binds_once_and_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []
    _patch_host(monkeypatch, calls)
    client = _FakeClient()
    first = ThemeController.for_client(client)
    second = ThemeController.for_client(client)
    assert first is second
    assert first.color_mode == "auto"
    assert first.theme is themes.BOOTSTRAP
    # runtime script injected once per client
    head_calls = [c for c in calls if c[0] == "head"]
    assert len(head_calls) == 1
    assert "ngbsSetColorMode" in head_calls[0][1]
    assert 'const themeStyleId = "ngbs-theme-client"' in head_calls[0][1]


def test_for_client_routes_head_and_javascript_to_target(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []
    targets: list[Any] = []
    _patch_host(monkeypatch, calls, targets)
    target = _FakeClient()
    ThemeController.for_client(target)
    controller = ThemeController.for_client(target)
    controller.set_color_mode("dark")
    assert targets
    assert all(client is target for client in targets)


def test_failed_runtime_injection_is_not_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import theme as theme_module
    from nicegui_bootstrap_components._host import client_store

    def fail_add(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("head injection failed")

    monkeypatch.setattr(theme_module, "add_head_html", fail_add)
    client = _FakeClient()
    with pytest.raises(RuntimeError, match="head injection failed"):
        ThemeController.for_client(client)
    assert "theme_controller" not in client_store(client)


def test_set_color_mode_emits_runtime_call(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []
    _patch_host(monkeypatch, calls)
    controller = ThemeController.for_client(_FakeClient())
    controller.set_color_mode("dark")
    assert controller.color_mode == "dark"
    js_codes = [code for kind, code in calls if kind == "js"]
    assert any('"dark"' in code for code in js_codes)
    with pytest.raises(ValueError):
        controller.set_color_mode("sepia")


def test_bind_to_nicegui_dark_switches_auto_source(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []
    _patch_host(monkeypatch, calls)
    controller = ThemeController.for_client(_FakeClient())
    controller.bind_to_nicegui_dark(False)
    js_codes = [code for kind, code in calls if kind == "js"]
    assert any("false" in code for code in js_codes)


def test_ensure_theme_bound_is_safe_without_page(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import theme as theme_module

    def boom() -> None:
        raise RuntimeError("no client")

    monkeypatch.setattr(theme_module, "client_store", boom)
    ensure_theme_bound()  # must not raise


def test_ensure_theme_bound_binds_on_first_use(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import theme as theme_module

    store: dict[str, Any] = {}
    calls: list[tuple[str, str]] = []
    _patch_host(monkeypatch, calls)
    monkeypatch.setattr(theme_module, "client_store", lambda *a, **k: store)
    monkeypatch.setattr(theme_module, "get_client", lambda: _FakeClient())
    ensure_theme_bound()
    assert "theme_controller" in store
    # second call is a no-op
    first = store["theme_controller"]
    ensure_theme_bound()
    assert store["theme_controller"] is first
