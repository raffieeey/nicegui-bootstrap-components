"""Per-client color mode and stylesheet selection."""

from __future__ import annotations

import json
from typing import Any

from . import themes as _themes
from ._host import add_head_html, client_store, get_client, run_javascript
from .assets import _validate_stylesheet_url, _validated_theme_cdn, get_asset_manager

__all__ = ["ThemeController"]

THEME_STYLE_ID = "ngbs-theme-client"

_MODE_VALUES = {"light", "dark", "auto"}

_RUNTIME_JS = r"""
(() => {
  if (window.ngbsSetColorMode) return;
  const themeStyleId = __NGBS_THEME_STYLE_ID__;
  const styleMode = __NGBS_STYLE_MODE__;
  let observer = null;
  let media = null;
  let domReadyHandler = null;
  let lastResolved = 'light';
  const targets = () => {
    if (styleMode === 'unscoped') {
      return document.documentElement ? [document.documentElement] : [];
    }
    return document.querySelectorAll('.ngbs, .ngbs-overlay');
  };
  const apply = (value) => {
    lastResolved = value;
    targets().forEach((el) => el.setAttribute('data-bs-theme', value));
  };
  const clearNiceguiObserver = () => {
    if (observer) { observer.disconnect(); observer = null; }
    if (domReadyHandler) {
      document.removeEventListener('DOMContentLoaded', domReadyHandler);
      domReadyHandler = null;
    }
  };
  const armNiceguiObserver = (read) => {
    const body = document.body;
    if (!body) {
      domReadyHandler = () => {
        domReadyHandler = null;
        armNiceguiObserver(read);
      };
      document.addEventListener('DOMContentLoaded', domReadyHandler, { once: true });
      return;
    }
    observer = new MutationObserver(() => apply(read() ? 'dark' : 'light'));
    observer.observe(body, { attributes: true, attributeFilter: ['class'] });
    apply(read() ? 'dark' : 'light');
  };
  window.ngbsApplyCurrentTheme = () => apply(lastResolved);
  window.ngbsSetColorMode = (mode, followNiceguiDark) => {
    clearNiceguiObserver();
    if (media) { media.removeEventListener('change', media._ngbsRun); media = null; }
    if (mode === 'light' || mode === 'dark') { apply(mode); return; }
    if (followNiceguiDark) {
      const read = () => document.body ? document.body.classList.contains('body--dark') : false;
      armNiceguiObserver(read);
      return;
    }
    media = window.matchMedia('(prefers-color-scheme: dark)');
    media._ngbsRun = () => apply(media.matches ? 'dark' : 'light');
    media.addEventListener('change', media._ngbsRun);
    media._ngbsRun();
  };
  const escapeCssString = (value) => value
    .replace(/\\/g, '\\\\')
    .replace(/"/g, '\\"')
    .replace(/\r/g, '\\D ')
    .replace(/\n/g, '\\A ');
  window.ngbsSetThemeSheet = (href) => {
    let tag = document.getElementById(themeStyleId);
    if (!tag) {
      tag = document.createElement('style');
      tag.id = themeStyleId;
      document.head.appendChild(tag);
    }
    tag.textContent = '@import url("' + escapeCssString(href) + '") layer(overrides);';
  };
})();
"""


def _runtime_js(style_mode: str) -> str:
    return _RUNTIME_JS.replace("__NGBS_THEME_STYLE_ID__", json.dumps(THEME_STYLE_ID)).replace(
        "__NGBS_STYLE_MODE__", json.dumps(style_mode)
    )


def _normalize_mode(mode: str | None) -> str:
    value = str(mode).lower()
    if value not in _MODE_VALUES:
        raise ValueError(f"color_mode must be light|dark|auto, got {mode!r}")
    return value


class ThemeController:
    """Page-lifetime theme state for one NiceGUI client.

    Obtained through :meth:`for_client`; never constructed directly.
    """

    def __init__(
        self,
        client: Any,
        *,
        color_mode: str,
        follow_nicegui_dark: bool,
        theme: _themes.Theme,
    ) -> None:
        self._client = client
        self._color_mode = color_mode
        self._follow_nicegui_dark = follow_nicegui_dark
        self._theme = theme

    @classmethod
    def for_client(cls, client: Any | None = None) -> ThemeController:
        """Bind or return the controller for ``client`` (defaults to the current one)."""
        target = client if client is not None else get_client()
        if target is None:
            raise RuntimeError("ThemeController requires an active client")
        store = client_store(target)
        existing = store.get("theme_controller")
        if isinstance(existing, cls):
            return existing
        manager = get_asset_manager()
        raw_mode = manager.color_mode if manager is not None else "auto"
        color_mode = _normalize_mode(raw_mode)
        style_mode = manager.mode.value if manager is not None else "mixed"
        controller = cls(
            target,
            color_mode=color_mode,
            follow_nicegui_dark=manager.follow_nicegui_dark if manager is not None else True,
            theme=manager.theme if manager is not None else _themes.BOOTSTRAP,
        )
        add_head_html(f"<script>{_runtime_js(style_mode)}</script>", shared=False, client=target)
        controller._apply()
        store["theme_controller"] = controller
        return controller

    # -- state ---------------------------------------------------------

    @property
    def color_mode(self) -> str:
        return self._color_mode

    @property
    def theme(self) -> _themes.Theme:
        return self._theme

    def set_color_mode(self, mode: str) -> None:
        """Switch this client to ``light``, ``dark``, or ``auto``."""
        self._color_mode = _normalize_mode(mode)
        self._apply()

    def set_theme(self, theme: _themes.Theme | str) -> None:
        """Swap this client's stylesheet without touching other clients."""
        resolved = _resolve_theme(theme)
        manager = get_asset_manager()
        href = _stylesheet_url(resolved, manager)
        if href is None:
            raise RuntimeError("bundled theme selection requires setup() to serve its stylesheet")
        run_javascript(
            f"window.ngbsSetThemeSheet && window.ngbsSetThemeSheet({json.dumps(href)});",
            client=self._client,
        )
        self._theme = resolved

    def bind_to_nicegui_dark(self, enabled: bool = True) -> None:
        """Choose whether ``auto`` follows the host dark state or the OS preference."""
        self._follow_nicegui_dark = bool(enabled)
        if self._color_mode == "auto":
            self._apply()

    # -- internals -----------------------------------------------------

    def _apply(self) -> None:
        mode = self._color_mode
        follow = "true" if self._follow_nicegui_dark else "false"
        run_javascript(
            f"window.ngbsSetColorMode && window.ngbsSetColorMode({json.dumps(mode)}, {follow});",
            client=self._client,
        )
        # Live anchors are updated by the runtime; the stored value seeds any
        # scope or overlay root created later in this client.
        store = client_store(self._client)
        store["overlay_theme"] = None if mode == "auto" else mode


def _resolve_theme(theme: _themes.Theme | str) -> _themes.Theme:
    if isinstance(theme, _themes.Theme):
        for candidate in _themes._CATALOGUE:
            if theme is candidate or theme == candidate:
                return candidate
        if theme.cdn:
            _validate_stylesheet_url(theme.cdn)
        elif not theme.bundled:
            raise ValueError("theme must provide a bundled name or a plain http(s) URL")
        return theme
    if isinstance(theme, str):
        for candidate in _themes._CATALOGUE:
            if theme in {candidate.name, candidate.bundled}:
                return candidate
        if theme.lower().startswith(("http://", "https://")):
            _validate_stylesheet_url(theme)
            return _themes.Theme(name=theme, cdn=theme, bundled="")
        valid_names = ", ".join(candidate.name for candidate in _themes._CATALOGUE)
        raise ValueError(f"unknown theme {theme!r}; valid names: {valid_names}")
    raise TypeError(f"theme must be a Theme or a name/url string, got {type(theme)!r}")


def _stylesheet_url(theme: _themes.Theme, manager: Any) -> str | None:
    if manager is not None and manager.cdn:
        return _validated_theme_cdn(theme)
    if not theme.bundled:
        return _validate_stylesheet_url(theme.cdn)
    return manager.bundled_url(theme) if manager is not None else None


def ensure_theme_bound() -> None:
    """Lazy-bind the controller on first library use inside a page."""
    try:
        store = client_store()
    except Exception:
        return
    if "theme_controller" in store:
        return
    try:
        ThemeController.for_client()
    except Exception:
        return
