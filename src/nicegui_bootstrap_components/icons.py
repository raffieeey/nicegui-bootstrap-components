"""Pinned icon stylesheet constants.

The bundled stylesheets include the font files referenced by the pinned CSS.
Bundled files are used by default. When permitted CDN mode is selected, icon
imports use their pinned jsDelivr URLs because icon selectors are
mode-independent; this does not relax the Mode B CDN guard for themes.
"""

from __future__ import annotations

from .themes import Theme

__all__ = ["BOOTSTRAP", "FONT_AWESOME", "IconTheme"]

IconTheme = Theme

_CDN_ROOT = "https://cdn.jsdelivr.net/npm"

BOOTSTRAP = IconTheme(
    name="bootstrap",
    cdn=f"{_CDN_ROOT}/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css",
    bundled="ngbs-icons-bootstrap",
)

FONT_AWESOME = IconTheme(
    name="fontawesome",
    cdn=(f"{_CDN_ROOT}/@fortawesome/fontawesome-free@6.7.2/css/all.min.css"),
    bundled="ngbs-icons-fontawesome",
)
