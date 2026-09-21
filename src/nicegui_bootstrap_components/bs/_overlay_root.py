"""Per-client ``#ngbs-overlay-root`` (body child, scope-anchor for overlays)."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from .._host import Element, client_store, html_id, is_deleted, run_javascript
from ..assets import StyleMode, get_mode

__all__ = [
    "OVERLAY_ROOT_ID",
    "get_or_create_overlay_root",
    "set_overlay_theme",
]

OVERLAY_ROOT_ID = "ngbs-overlay-root"


def get_or_create_overlay_root() -> Any:
    """Return the per-client overlay portal root, creating it on first use.

    Classes: ``ngbs ngbs-overlay``. DOM id: ``#ngbs-overlay-root``.
    Mode B applies ``z-index: 5000`` so Bootstrap's internal scale stacks inside.
    """
    store = client_store()
    existing = store.get("overlay_root")
    if existing is not None and not is_deleted(existing):
        return existing
    root = Element("div")
    root.classes("ngbs ngbs-overlay")
    root.props(f"id={OVERLAY_ROOT_ID}")
    theme = store.get("overlay_theme")
    if theme:
        root.props(f"data-bs-theme={theme}")
    mode = get_mode()
    if mode is not StyleMode.UNSCOPED:
        root.style("z-index: 5000")
    store["overlay_root"] = root
    hid = html_id(root)
    js = (
        "(() => {"
        f"const el = document.getElementById({json.dumps(OVERLAY_ROOT_ID)}) "
        f"|| document.getElementById({json.dumps(hid)});"
        "if (!el) return;"
        f"el.id = {json.dumps(OVERLAY_ROOT_ID)};"
        "document.body.appendChild(el);"
        "})();"
    )
    response = run_javascript(js)
    fire = getattr(response, "_fire", None)
    if fire is not None:
        task = asyncio.ensure_future(fire())
        task.add_done_callback(lambda _t: None)
    return root


def ensure_overlay_root() -> Any:
    """Alias of :func:`get_or_create_overlay_root` (overlays contract name)."""
    return get_or_create_overlay_root()


def set_overlay_theme(theme: str | None) -> None:
    """Set or remove ``data-bs-theme`` on the overlay root."""
    store = client_store()
    cleaned = theme if theme else None
    store["overlay_theme"] = cleaned
    root = get_or_create_overlay_root()
    if cleaned is None:
        root.props(remove="data-bs-theme")
    else:
        root.props(f"data-bs-theme={cleaned}")
