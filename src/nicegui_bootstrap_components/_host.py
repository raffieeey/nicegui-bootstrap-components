"""NiceGUI host adapter.

Every NiceGUI import used by this library goes through this module so host
upgrades touch a single file. Other packages must import Element, client
access, asset injection, and move helpers from here — never from ``nicegui``.
"""

from __future__ import annotations

import json
from typing import Any
from weakref import WeakKeyDictionary

from nicegui import core as ng_core
from nicegui import ui
from nicegui.element import Element as UiElement
from nicegui.elements.mixins.value_element import ValueElement as UiValueElement

try:
    from nicegui import context as ng_context
except ImportError:  # pragma: no cover - host layout varies by version
    ng_context = None  # type: ignore[assignment]

__all__ = [
    "Element",
    "UiElement",
    "ValueElement",
    "add_css",
    "add_head_html",
    "add_static_files",
    "client_store",
    "create_text_span",
    "get_app",
    "get_client",
    "get_parent",
    "get_slot_parent",
    "html_id",
    "is_deleted",
    "is_ui_element",
    "move_element",
    "run_javascript",
    "set_element_text",
]

_STORE_KEY = "nicegui_bootstrap_components"
_WEAK_STORES: WeakKeyDictionary[Any, dict[str, Any]] = WeakKeyDictionary()
_ID_STORES: dict[int, dict[str, Any]] = {}


class Element(UiElement):
    """``ui.element`` wrapper that honors ``_desired_tag`` set before init.

    Custom Vue components still use NiceGUI class kwargs on subclasses::

        class Foo(Element, component="foo.js", dependencies=[...], esm={...}):
            ...

    Do not call ``register_importmap_override('vue', ...)``.
    """

    def __init__(
        self,
        tag: str = "div",
        *,
        _client: Any | None = None,
        _parent_slot: Any | None = None,
    ) -> None:
        override = getattr(self, "_desired_tag", None)
        if isinstance(override, str) and override:
            tag = override
        kwargs: dict[str, Any] = {}
        if _client is not None:
            kwargs["_client"] = _client
        if _parent_slot is not None:
            kwargs["_parent_slot"] = _parent_slot
        super().__init__(tag, **kwargs)


class ValueElement(UiValueElement):
    """ValueElement adapter that honors ``_desired_tag`` (tag is not forwarded by NiceGUI)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        desired = getattr(self, "_desired_tag", None)
        if not isinstance(desired, str) or not desired:
            super().__init__(*args, **kwargs)
            return
        original = UiElement.__init__

        def patched(instance: Any, tag: str = "div", *rest: Any, **kw: Any) -> None:
            original(instance, desired, *rest, **kw)

        UiElement.__init__ = patched  # type: ignore[assignment]
        try:
            super().__init__(*args, **kwargs)
        finally:
            UiElement.__init__ = original  # type: ignore[method-assign]


def _ng_context() -> Any:
    ctx = getattr(ui, "context", None)
    if ctx is not None:
        return ctx
    if ng_context is not None:
        return ng_context
    raise RuntimeError("NiceGUI context is unavailable")


def add_head_html(
    html: str,
    *,
    shared: bool = True,
    client: Any | None = None,
) -> None:
    """Inject HTML into page ``<head>``. ``shared=True`` applies to all templates."""
    if client is not None and shared:
        raise ValueError("a client cannot be combined with shared head HTML")
    if client is not None:
        if getattr(client, "_response_built", False) and not getattr(client, "is_deleted", False):
            client.run_javascript(
                f'document.head.insertAdjacentHTML("beforeend", {json.dumps(html)});'
            )
        client._head_html += html + "\n"
        return
    try:
        ui.add_head_html(html, shared=shared)
    except TypeError:
        ui.add_head_html(html)


def add_css(css: str, *, shared: bool = True) -> None:
    """Inject CSS via NiceGUI. Library styles must not use this unlayered path."""
    try:
        ui.add_css(css, shared=shared)
    except TypeError:
        ui.add_css(css)


def add_static_files(url_path: str, local_directory: str) -> None:
    """Serve a local directory at ``url_path`` on the NiceGUI app."""
    ng_core.app.add_static_files(url_path, local_directory)


def get_app() -> Any:
    """Return the NiceGUI app singleton."""
    return ng_core.app


def get_client() -> Any:
    """Return the current NiceGUI client."""
    return _ng_context().client


def get_slot_parent() -> Any | None:
    """Return the parent element of the current slot, or ``None`` if unavailable."""
    try:
        slot = _ng_context().slot
    except Exception:
        return None
    if slot is None:
        return None
    return getattr(slot, "parent", None)


def move_element(
    element: Any,
    target_container: Any | None = None,
    target_index: int = -1,
    target_slot: str = "",
) -> None:
    """Reparent ``element`` using NiceGUI ``Element.move``."""
    element.move(target_container, target_index, target_slot=target_slot or None)


def client_store(client: Any | None = None) -> dict[str, Any]:
    """Return the per-client dict used for public ids, overlay root, and theme."""
    if client is None:
        client = get_client()
    extras = getattr(client, "extras", None)
    if extras is None:
        try:
            extras = {}
            client.extras = extras
        except (AttributeError, TypeError):
            extras = None
    if isinstance(extras, dict):
        bucket = extras.get(_STORE_KEY)
        if bucket is None:
            bucket = {}
            extras[_STORE_KEY] = bucket
        return bucket
    try:
        store = _WEAK_STORES.get(client)
        if store is None:
            store = {}
            _WEAK_STORES[client] = store
        return store
    except TypeError:
        store = _ID_STORES.get(id(client))
        if store is None:
            store = {}
            _ID_STORES[id(client)] = store
        return store


def run_javascript(code: str, *, client: Any | None = None) -> Any:
    """Run JavaScript on the given or current client."""
    target = client if client is not None else get_client()
    return target.run_javascript(code)


def html_id(element: Any) -> str:
    """Return the DOM id NiceGUI assigned to ``element``."""
    hid = getattr(element, "html_id", None)
    if isinstance(hid, str) and hid:
        return hid
    return f"c{getattr(element, 'id', '')}"


def is_deleted(element: Any) -> bool:
    """Return True if the element has been deleted."""
    if getattr(element, "_deleted", False):
        return True
    client = getattr(element, "client", None)
    ident = getattr(element, "id", None)
    elements = getattr(client, "elements", None) if client is not None else None
    return bool(isinstance(elements, dict) and ident is not None and ident not in elements)


def is_ui_element(obj: object) -> bool:
    """Return True if ``obj`` is a NiceGUI element."""
    return isinstance(obj, UiElement)


def get_parent(element: Any) -> Any | None:
    """Return the Python parent element, if any."""
    slot = getattr(element, "parent_slot", None)
    if slot is None:
        return None
    return getattr(slot, "parent", None)


def set_element_text(element: Any, text: str) -> None:
    """Set default-slot text without assigning ``innerHTML``.

    Mirrors into ``props['text']`` so NiceGUI's testing helpers
    (``ElementFilter``) can find elements by content: the filter reads
    ``props['text']``/``TextElement.text`` and a plain ``Element``'s
    ``_text`` is invisible to it.
    """
    element._text = text
    element._props["text"] = text


def create_text_span(text: str) -> Element:
    """Create a ``span.ngbs-text`` carrying ``text``."""
    span = Element("span")
    span.classes("ngbs-text")
    set_element_text(span, text)
    return span
