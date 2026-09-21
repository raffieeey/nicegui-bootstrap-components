"""Process-level CSS/JS registration (idempotent ``setup()``)."""

from __future__ import annotations

import enum
import re
from contextlib import ExitStack
from importlib.resources import as_file, files
from typing import Any, Literal
from urllib.parse import urlsplit

from . import icons as _icons
from . import themes as _themes
from ._host import add_head_html, add_static_files

__all__ = [
    "AssetManager",
    "StyleMode",
    "get_asset_manager",
    "get_mode",
    "setup",
]

STATIC_URL_PREFIX = "/_nicegui_bootstrap_components/static"
DIST_CSS_DIR = "dist"
PROTOTYPE_CSS_NAME = "prototype-ngbs.css"
_COMPAT_CSS_NAME = "ngbs-compat.css"
_COMPAT_CSS_NAME_UNSCOPED = "ngbs-compat-unscoped.css"
_HOST_CSS_NAME = "ngbs-host.css"
_HOST_CSS_NAME_UNSCOPED = "ngbs-host-unscoped.css"
_BOOTSTRAP_CDN = _themes.BOOTSTRAP.cdn

_FORBIDDEN_URL_CHARACTERS = frozenset("\"'{}\\;()<>@")

_MANAGER: AssetManager | None = None


class StyleMode(str, enum.Enum):
    """CSS coexistence mode.

    ``UNSCOPED`` is Mode A (Bootstrap-first). ``MIXED`` is Mode B (scoped islands).
    """

    UNSCOPED = "unscoped"
    MIXED = "mixed"


def _read_prototype_css() -> str:
    try:
        resource = files("nicegui_bootstrap_components").joinpath("static", PROTOTYPE_CSS_NAME)  # type: ignore[call-arg]
        return resource.read_text(encoding="utf-8")
    except (OSError, ModuleNotFoundError, AttributeError, UnicodeError):
        return "/* prototype-ngbs.css missing from package data */\n"


def _validate_stylesheet_url(value: str) -> str:
    """Validate a stylesheet URL before it reaches CSS or JavaScript."""
    if not isinstance(value, str):
        raise TypeError(f"theme URL must be a string, got {type(value)!r}")
    if not value or any(char.isspace() or char in _FORBIDDEN_URL_CHARACTERS for char in value):
        raise ValueError(
            "theme URL must be a plain http(s) URL without whitespace or CSS delimiters"
        )
    parsed = urlsplit(value)
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"theme URL must be a plain http(s) URL, got {value!r}")
    return value


def _css_string(value: str) -> str:
    return (
        value.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\D ").replace("\n", "\\A ")
    )


def _layered_imports(hrefs: list[str]) -> str:
    imports = "".join(f'@import url("{_css_string(href)}") layer(overrides);' for href in hrefs)
    return f"<style>{imports}</style>"


def _layered_import(href: str) -> str:
    return _layered_imports([href])


def _validated_theme_cdn(theme: _themes.Theme) -> str:
    for candidate in _themes._CATALOGUE:
        if theme is candidate or theme == candidate:
            return candidate.cdn
    return _validate_stylesheet_url(theme.cdn)


def _resolve_icons(icons: _icons.IconTheme | str | None) -> _icons.IconTheme | None:
    if icons is None:
        return None
    candidates = (_icons.BOOTSTRAP, _icons.FONT_AWESOME)
    if isinstance(icons, _icons.IconTheme):
        for candidate in candidates:
            if icons is candidate or icons == candidate:
                return candidate
        raise ValueError("icons must be bootstrap or fontawesome")
    if isinstance(icons, str):
        for candidate in candidates:
            if icons in {candidate.name, candidate.bundled}:
                return candidate
        raise ValueError(f"unknown icon set {icons!r}; valid names: bootstrap, fontawesome")
    raise TypeError(f"icons must be an icon theme, a name string, or None, got {type(icons)!r}")


def _validated_icon_cdn(icon: _icons.IconTheme) -> str:
    for candidate in (_icons.BOOTSTRAP, _icons.FONT_AWESOME):
        if icon is candidate or icon == candidate:
            return candidate.cdn
    return _validate_stylesheet_url(icon.cdn)


def _unscoped_payload(css: str) -> str:
    """Derive the Mode A (Bootstrap-first) global stylesheet.

    The prototype stylesheet is authored with an ``.ngbs`` scope prefix
    (Mode B). Mode A applies the same rules to the real document:
    strip the scope prefixes so Reboot targets ``:root``/``html``.
    """
    out = css.replace(".ngbs {", ":root {")
    out = out.replace(".ngbs,", ":root,")
    out = out.replace(".ngbs[data-bs-theme=", "[data-bs-theme=")
    out = out.replace(".ngbs *", "*")
    out = out.replace(".ngbs ", "")
    out = re.sub(r"\.ngbs(?![-\w])", ":root", out)
    return out


class AssetManager:
    """Process-level defaults and idempotent layered CSS injection."""

    def __init__(
        self,
        mode: StyleMode,
        *,
        cdn: bool = False,
        theme: _themes.Theme | None = None,
        icons: _icons.IconTheme | None = None,
        color_mode: str = "auto",
        follow_nicegui_dark: bool = True,
    ) -> None:
        self.mode = mode
        self.cdn = cdn
        self.theme = theme if theme is not None else _themes.BOOTSTRAP
        self.icons = icons
        self.color_mode = color_mode
        self.follow_nicegui_dark = follow_nicegui_dark
        self._injected = False
        self._stack = ExitStack()
        self._static_registered = False

    def close(self) -> None:
        """Release extracted package resources."""
        self._stack.close()

    def bundled_url(self, theme: _themes.Theme) -> str | None:
        """Register the package stylesheet directory and return a theme's URL."""
        located = self._locate_bundled_theme(theme)
        if located is None:
            return None
        rel, _resource = located
        self._register_static()
        return f"{STATIC_URL_PREFIX}/{rel}"

    def _register_static(self) -> None:
        if self._static_registered:
            return
        resource = files("nicegui_bootstrap_components").joinpath("static")
        path = self._stack.enter_context(as_file(resource))
        add_static_files(STATIC_URL_PREFIX, str(path))
        self._static_registered = True

    def _built_theme_path(self, theme: _themes.Theme) -> str | None:
        if not theme.bundled:
            return None
        suffix = "" if self.mode is not StyleMode.UNSCOPED else "-unscoped"
        return f"{DIST_CSS_DIR}/{theme.bundled}{suffix}.css"

    def _built_icon_path(self, icon: _icons.IconTheme) -> str | None:
        if not icon.bundled:
            return None
        return f"{DIST_CSS_DIR}/{icon.bundled}.css"

    def _locate_bundled_theme(self, theme: _themes.Theme) -> tuple[str, Any] | None:
        rel = self._built_theme_path(theme)
        if rel is None:
            return None
        try:
            resource = files("nicegui_bootstrap_components").joinpath("static", rel)  # type: ignore[call-arg]
            exists = resource.is_file()
        except (OSError, ModuleNotFoundError, AttributeError, TypeError, ValueError) as exc:
            raise FileNotFoundError(f"bundled stylesheet not found: {rel}") from exc
        if not exists:
            raise FileNotFoundError(f"bundled stylesheet not found: {rel}")
        return rel, resource

    def _optional_bundled_url(self, rel: str) -> str | None:
        try:
            resource = files("nicegui_bootstrap_components").joinpath("static", rel)  # type: ignore[call-arg]
            if not resource.is_file():
                return None
            self._register_static()
            self._stack.enter_context(as_file(resource))
        except (OSError, ModuleNotFoundError, AttributeError, TypeError, ValueError):
            return None
        return f"{STATIC_URL_PREFIX}/{rel}"

    def _inject_optional_import(self, rel: str) -> bool:
        href = self._optional_bundled_url(rel)
        if href is None:
            return False
        add_head_html(_layered_import(href), shared=True)
        return True

    def _inject_theme(self) -> bool:
        """Import the built stylesheet pair via the cascade layer. True if served as a file."""
        located = self._locate_bundled_theme(self.theme)
        if located is None:
            return False
        rel, resource = located
        self._register_static()
        self._stack.enter_context(as_file(resource))
        href = f"{STATIC_URL_PREFIX}/{rel}"
        add_head_html(_layered_import(href), shared=True)
        compat_name = (
            _COMPAT_CSS_NAME_UNSCOPED if self.mode is StyleMode.UNSCOPED else _COMPAT_CSS_NAME
        )
        compat_rel = f"{DIST_CSS_DIR}/{compat_name}"
        self._inject_optional_import(compat_rel)
        host_name = _HOST_CSS_NAME_UNSCOPED if self.mode is StyleMode.UNSCOPED else _HOST_CSS_NAME
        self._inject_optional_import(f"{DIST_CSS_DIR}/{host_name}")
        return True

    def _inject_icons(self) -> None:
        if self.icons is None:
            return
        if self.cdn:
            add_head_html(_layered_import(_validated_icon_cdn(self.icons)), shared=True)
            return
        rel = self._built_icon_path(self.icons)
        if rel is None or not self._inject_optional_import(rel):
            raise FileNotFoundError(f"bundled icon stylesheet not found: {rel}")

    def inject(self) -> None:
        """Inject library CSS into ``layer(overrides)``. Duplicate calls are no-ops."""
        if self._injected:
            return
        if self.cdn:
            imports = [_validated_theme_cdn(self.theme)]
            host_name = (
                _HOST_CSS_NAME_UNSCOPED if self.mode is StyleMode.UNSCOPED else _HOST_CSS_NAME
            )
            host_href = self._optional_bundled_url(f"{DIST_CSS_DIR}/{host_name}")
            if host_href is not None:
                imports.append(host_href)
            add_head_html(_layered_imports(imports), shared=True)
            self._inject_icons()
            self._injected = True
            return
        if self._inject_theme():
            self._inject_icons()
            self._injected = True
            return
        injected_import = False
        if self.mode is not StyleMode.UNSCOPED:
            try:
                resource = files("nicegui_bootstrap_components").joinpath(
                    "static", PROTOTYPE_CSS_NAME
                )  # type: ignore[call-arg]
                path = self._stack.enter_context(as_file(resource))
                add_static_files(STATIC_URL_PREFIX, str(path.parent))
                href = f"{STATIC_URL_PREFIX}/{PROTOTYPE_CSS_NAME}"
                add_head_html(_layered_import(href), shared=True)
                injected_import = True
            except (OSError, ModuleNotFoundError, AttributeError, TypeError, ValueError):
                injected_import = False
        if not injected_import:
            css = _read_prototype_css()
            if self.mode is StyleMode.UNSCOPED:
                css = _unscoped_payload(css)
            payload = css if "@layer overrides" in css else f"@layer overrides {{\n{css}\n}}"
            add_head_html(f"<style>\n{payload}\n</style>", shared=True)
        host_name = _HOST_CSS_NAME_UNSCOPED if self.mode is StyleMode.UNSCOPED else _HOST_CSS_NAME
        self._inject_optional_import(f"{DIST_CSS_DIR}/{host_name}")
        self._inject_icons()
        self._injected = True


def get_mode() -> StyleMode | None:
    """Return the process-wide style mode, or ``None`` if ``setup()`` was not called."""
    if _MANAGER is None:
        return None
    return _MANAGER.mode


def get_asset_manager() -> AssetManager | None:
    """Return the process-level manager, or ``None`` if ``setup()`` was not called."""
    return _MANAGER


def setup(
    mode: StyleMode = StyleMode.MIXED,
    *,
    theme: _themes.Theme | str = _themes.BOOTSTRAP,
    icons: Literal["bootstrap", "fontawesome"] | _icons.IconTheme | None = None,
    color_mode: str | None = "auto",
    cdn: bool = False,
    follow_nicegui_dark: bool = True,
) -> None:
    """Register library CSS once (process-wide).

    Idempotent when called again with the same arguments. Raises ``ValueError``
    on a conflicting mode or option, or when Mode B (scoped) is combined with
    ``cdn=True``. Does not bind to a client.
    """
    global _MANAGER
    if not isinstance(mode, StyleMode):
        mode = StyleMode(mode)
    if cdn and mode is not StyleMode.UNSCOPED:
        raise ValueError("cdn=True requires mode=StyleMode.UNSCOPED (scoped builds are bundled)")
    from .theme import _normalize_mode, _resolve_theme

    normalized_color_mode = _normalize_mode(color_mode)
    resolved_theme = _resolve_theme(theme)
    resolved_icons = _resolve_icons(icons)
    normalized_follow = bool(follow_nicegui_dark)
    if _MANAGER is not None:
        if _MANAGER.mode != mode:
            raise ValueError(
                f"setup() already called with mode={_MANAGER.mode!r}; cannot change to {mode!r}"
            )
        conflicts: list[str] = []
        if _MANAGER.theme != resolved_theme:
            conflicts.append("theme")
        if _MANAGER.icons != resolved_icons:
            conflicts.append("icons")
        if _MANAGER.color_mode != normalized_color_mode:
            conflicts.append("color_mode")
        if _MANAGER.cdn != cdn:
            conflicts.append("cdn")
        if _MANAGER.follow_nicegui_dark != normalized_follow:
            conflicts.append("follow_nicegui_dark")
        if conflicts:
            names = ", ".join(conflicts)
            raise ValueError(f"setup() already called with conflicting argument(s): {names}")
        return

    manager = AssetManager(
        mode,
        cdn=cdn,
        theme=resolved_theme,
        icons=resolved_icons,
        color_mode=normalized_color_mode,
        follow_nicegui_dark=normalized_follow,
    )
    try:
        manager.inject()
    except Exception:
        manager.close()
        raise
    _MANAGER = manager


def _reset_setup() -> None:
    global _MANAGER
    if _MANAGER is not None:
        _MANAGER.close()
    _MANAGER = None
