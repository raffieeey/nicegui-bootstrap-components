"""Adapted persistence helpers and navigation policy."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from . import _host

__all__ = [
    "persist_key",
    "validate_persist",
    "storage_name",
    "read_persisted",
    "write_persisted",
    "restore_value",
    "navigation_kind",
    "apply_navigation",
]

_LOG = logging.getLogger(__name__)
_ALLOWED_PERSIST = frozenset({"off", "local", "session"})
_LOGGED_INVALID_KEYS: set[str] = set()


def persist_key(element_id: str, prop: str) -> str:
    """Return the storage key ``ngbs:{id}:{prop}``."""
    return f"ngbs:{element_id}:{prop}"


def validate_persist(persist: str, *, element_id: str | None, prop: str) -> None:
    """Raise ``ValueError`` when ``persist`` or ``element_id`` is not valid."""
    if persist not in _ALLOWED_PERSIST:
        raise ValueError(f"persist must be 'off', 'local', or 'session', got {persist!r}")
    if persist != "off" and not element_id:
        raise ValueError(f"persist={persist!r} requires a public id for prop {prop!r}")


def storage_name(persist: str) -> str | None:
    """Return the Web Storage object name for ``persist``, or ``None`` when off."""
    if persist == "local":
        return "localStorage"
    if persist == "session":
        return "sessionStorage"
    return None


def _log_invalid(key: str, reason: str) -> None:
    if key in _LOGGED_INVALID_KEYS:
        return
    _LOGGED_INVALID_KEYS.add(key)
    _LOG.debug("Ignoring invalid persisted value for %s (%s)", key, reason)


def _type_matches(value: Any, default: Any) -> bool:
    if default is None:
        return True
    return type(value) is type(default)


def _decode_stored(raw: Any, default: Any, key: str) -> Any:
    if raw is None:
        return default
    if isinstance(raw, str):
        try:
            value: Any = json.loads(raw)
        except json.JSONDecodeError:
            _log_invalid(key, "invalid JSON")
            return default
    else:
        value = raw
    if not _type_matches(value, default):
        _log_invalid(key, "wrong type")
        return default
    return value


def _execute_javascript(code: str, client: Any) -> Any:
    run_javascript: Any = _host.run_javascript
    return run_javascript(code, client=client)


def read_persisted(
    persist: str,
    element_id: str,
    prop: str,
    default: Any,
    *,
    client: Any | None = None,
) -> Any:
    """Read a persisted value from Web Storage.

    When ``persist`` is ``off`` or ``client`` is ``None``, return ``default``
    without touching storage. Invalid JSON or a value whose type does not match
    ``default`` yields ``default`` and a single debug log per key.
    """
    validate_persist(persist, element_id=element_id, prop=prop)
    name = storage_name(persist)
    if name is None or client is None:
        return default
    key = persist_key(element_id, prop)
    code = f"window.{name}.getItem({json.dumps(key)})"
    raw = _execute_javascript(code, client)
    return _decode_stored(raw, default, key)


def write_persisted(
    persist: str,
    element_id: str,
    prop: str,
    value: Any,
    *,
    client: Any | None = None,
) -> None:
    """Write ``value`` to Web Storage.

    No-op when ``persist`` is ``off`` or ``client`` is ``None``.
    """
    validate_persist(persist, element_id=element_id, prop=prop)
    name = storage_name(persist)
    if name is None or client is None:
        return
    key = persist_key(element_id, prop)
    code = f"window.{name}.setItem({json.dumps(key)}, JSON.stringify({json.dumps(value)}))"
    _execute_javascript(code, client)


def restore_value(
    persist: str,
    element_id: str,
    prop: str,
    default: Any,
    *,
    client: Any | None = None,
) -> Any:
    """Return the stored value or ``default`` without writing back.

    Callers must apply the result silently: do not fire ``on_change`` and do not
    persist the restored value (that would create a restore/write loop).
    """
    return read_persisted(persist, element_id, prop, default, client=client)


def navigation_kind(href: str | None, external_link: bool | None) -> str:
    """Return ``external``, ``internal``, or ``none`` for an href policy."""
    if not href:
        return "none"
    if external_link is True:
        return "external"
    if href.startswith(("http://", "https://", "//")):
        return "external"
    return "internal"


def _click_handler(
    on_click: Callable[..., Any] | None,
    navigate_to: str | None,
) -> Callable[..., None]:
    def _handler(*_args: Any, **_kwargs: Any) -> None:
        if on_click is not None:
            on_click()
        if navigate_to is not None:
            from nicegui import ui

            ui.navigate.to(navigate_to)

    return _handler


def apply_navigation(
    element: Any,
    href: str | None,
    external_link: bool | None,
    on_click: Callable[..., Any] | None,
) -> None:
    """Wire ``href``, ``target``, click handling, and in-app navigation.

    Buttons never receive ``href``, ``target``, or ``external_link``. External
    links keep a real ``href``/``target`` and do not call ``ui.navigate``.
    Internal links set ``href`` and navigate after ``on_click``.
    """
    kind = navigation_kind(href, external_link)
    tag = getattr(element, "tag", None)
    if isinstance(tag, str) and tag.lower() == "button":
        if on_click is not None:
            element.on("click", _click_handler(on_click, None))
        return

    if kind != "none" and href is not None:
        element._props["href"] = href
        if kind == "external":
            element._props["target"] = "_blank"

    if kind == "internal" and href:
        element.on("click", _click_handler(on_click, href))
        return

    if on_click is not None:
        element.on("click", _click_handler(on_click, None))
