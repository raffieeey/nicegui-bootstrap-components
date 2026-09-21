"""L1 tests for persistence and navigation helpers."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import pytest
from nicegui import ui

from nicegui_bootstrap_components.persist import (
    apply_navigation,
    navigation_kind,
    persist_key,
    read_persisted,
    restore_value,
    storage_name,
    validate_persist,
    write_persisted,
)


class _NavElement:
    def __init__(self, tag: str) -> None:
        self.tag = tag
        self._props: dict[str, Any] = {}
        self._handlers: list[tuple[str, Callable[..., Any]]] = []

    def on(self, event: str, handler: Callable[..., Any]) -> None:
        self._handlers.append((event, handler))


def _install_js(monkeypatch: pytest.MonkeyPatch, result: Any = None) -> list[str]:
    calls: list[str] = []

    def fake_run_javascript(
        code: str,
        client: object | None = None,
        **_kwargs: Any,
    ) -> Any:
        calls.append(code)
        return result

    monkeypatch.setattr(
        "nicegui_bootstrap_components._host.run_javascript",
        fake_run_javascript,
        raising=False,
    )
    return calls


def test_persist_key_format() -> None:
    assert persist_key("nav-1", "active_item") == "ngbs:nav-1:active_item"
    assert persist_key("box", "value") == "ngbs:box:value"


def test_validate_persist_off_without_id() -> None:
    validate_persist("off", element_id=None, prop="value")
    validate_persist("off", element_id="", prop="value")
    validate_persist("local", element_id="box", prop="value")
    validate_persist("session", element_id="box", prop="active_tab")


def test_validate_persist_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="must be"):
        validate_persist("disk", element_id="box", prop="value")
    with pytest.raises(ValueError, match="must be"):
        read_persisted("memory", "box", "value", 0)
    with pytest.raises(ValueError, match="must be"):
        write_persisted("memory", "box", "value", 1)


@pytest.mark.parametrize("persist_mode", ["local", "session"])
@pytest.mark.parametrize("element_id", [None, ""])
def test_validate_persist_requires_id(persist_mode: str, element_id: str | None) -> None:
    with pytest.raises(ValueError, match="public id"):
        validate_persist(persist_mode, element_id=element_id, prop="value")
    with pytest.raises(ValueError, match="public id"):
        read_persisted(persist_mode, element_id or "", "value", 0)
    with pytest.raises(ValueError, match="public id"):
        write_persisted(persist_mode, element_id or "", "value", 1)


@pytest.mark.parametrize(
    ("persist_mode", "expected"),
    [
        ("off", None),
        ("local", "localStorage"),
        ("session", "sessionStorage"),
    ],
)
def test_storage_name_mapping(persist_mode: str, expected: str | None) -> None:
    assert storage_name(persist_mode) == expected


def test_persist_off_no_storage_interaction(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _install_js(monkeypatch, result="99")
    dummy = object()
    assert read_persisted("off", "id", "value", 1, client=dummy) == 1
    write_persisted("off", "id", "value", 2, client=dummy)
    assert restore_value("off", "id", "value", 3, client=dummy) == 3
    assert calls == []


def test_read_without_client_returns_default() -> None:
    assert read_persisted("local", "box", "value", 8) == 8
    assert restore_value("session", "box", "value", "fallback") == "fallback"


def test_write_without_client_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _install_js(monkeypatch)
    write_persisted("local", "box", "value", 8)
    assert calls == []


def test_restore_does_not_write(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _install_js(monkeypatch, result="4")
    dummy = object()
    assert restore_value("local", "box", "value", 0, client=dummy) == 4
    assert calls
    assert all("setItem" not in script for script in calls)
    assert any("getItem" in script for script in calls)


def test_invalid_json_keeps_default_and_logs_once(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG, logger="nicegui_bootstrap_components.persist")
    _install_js(monkeypatch, result="{")
    dummy = object()
    assert read_persisted("local", "bad-json", "value", 5, client=dummy) == 5
    assert read_persisted("local", "bad-json", "value", 5, client=dummy) == 5
    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "nicegui_bootstrap_components.persist"
        and record.levelno == logging.DEBUG
        and "ngbs:bad-json:value" in record.getMessage()
    ]
    assert len(messages) == 1
    assert "invalid JSON" in messages[0]


def test_wrong_type_keeps_default_and_logs_once(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG, logger="nicegui_bootstrap_components.persist")
    _install_js(monkeypatch, result=1)
    dummy = object()
    assert read_persisted("session", "bad-type", "value", "fallback", client=dummy) == "fallback"
    assert read_persisted("session", "bad-type", "value", "fallback", client=dummy) == "fallback"
    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "nicegui_bootstrap_components.persist"
        and "ngbs:bad-type:value" in record.getMessage()
    ]
    assert len(messages) == 1
    assert "wrong type" in messages[0]


def test_read_persisted_returns_decoded_value(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _install_js(monkeypatch, result='{"a": 1}')
    dummy = object()
    assert read_persisted("local", "ok", "value", {}, client=dummy) == {"a": 1}
    assert len(calls) == 1
    assert "localStorage" in calls[0]
    assert "getItem" in calls[0]
    assert "ngbs:ok:value" in calls[0]
    assert "setItem" not in calls[0]


def test_write_persisted_composes_set_item(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _install_js(monkeypatch)
    write_persisted("session", "sid", "active_tab", "t2", client=object())
    assert len(calls) == 1
    script = calls[0]
    assert "sessionStorage" in script
    assert "setItem" in script
    assert "ngbs:sid:active_tab" in script
    assert "getItem" not in script


def test_missing_key_keeps_default_without_log(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG, logger="nicegui_bootstrap_components.persist")
    _install_js(monkeypatch, result=None)
    assert read_persisted("local", "missing-key", "value", 7, client=object()) == 7
    persist_records = [
        record
        for record in caplog.records
        if record.name == "nicegui_bootstrap_components.persist"
        and "ngbs:missing-key:value" in record.getMessage()
    ]
    assert persist_records == []


@pytest.mark.parametrize(
    ("href", "external_link", "expected"),
    [
        (None, None, "none"),
        (None, True, "none"),
        ("", False, "none"),
        ("http://example.com", None, "external"),
        ("https://example.com", False, "external"),
        ("//cdn.example.com/lib.js", None, "external"),
        ("/internal", None, "internal"),
        ("/internal", False, "internal"),
        ("/internal", True, "external"),
        ("relative", None, "internal"),
        ("#hash", None, "internal"),
    ],
)
def test_navigation_kind_table(href: str | None, external_link: bool | None, expected: str) -> None:
    assert navigation_kind(href, external_link) == expected


def test_apply_navigation_href_when_appropriate() -> None:
    none_el = _NavElement("a")
    apply_navigation(none_el, None, None, None)
    assert "href" not in none_el._props
    assert "target" not in none_el._props
    assert none_el._handlers == []

    internal = _NavElement("a")
    apply_navigation(internal, "/home", False, None)
    assert internal._props.get("href") == "/home"
    assert "target" not in internal._props
    assert "external_link" not in internal._props

    external = _NavElement("a")
    apply_navigation(external, "https://example.com", None, None)
    assert external._props.get("href") == "https://example.com"
    assert external._props.get("target") == "_blank"
    assert "external_link" not in external._props

    proto = _NavElement("a")
    apply_navigation(proto, "//cdn.example.com/x.js", None, None)
    assert proto._props.get("href") == "//cdn.example.com/x.js"
    assert proto._props.get("target") == "_blank"


def test_button_never_receives_external_link() -> None:
    el = _NavElement("button")
    apply_navigation(el, "https://example.com", True, None)
    assert "href" not in el._props
    assert "target" not in el._props
    assert "external_link" not in el._props
    assert el._handlers == []

    clicked: list[int] = []
    with_click = _NavElement("button")
    apply_navigation(with_click, "/internal", False, lambda: clicked.append(1))
    assert "href" not in with_click._props
    assert "target" not in with_click._props
    assert "external_link" not in with_click._props
    assert len(with_click._handlers) == 1
    with_click._handlers[0][1]()
    assert clicked == [1]


def test_internal_link_click_invokes_on_click_then_navigates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    order: list[object] = []

    def fake_to(target: str, *_args: Any, **_kwargs: Any) -> None:
        order.append(("nav", target))

    monkeypatch.setattr(ui.navigate, "to", fake_to)
    el = _NavElement("a")
    apply_navigation(el, "/home", False, lambda: order.append("click"))
    assert el._props.get("href") == "/home"
    assert len(el._handlers) == 1
    assert el._handlers[0][0] == "click"
    el._handlers[0][1]()
    assert order == ["click", ("nav", "/home")]


def test_external_link_does_not_register_navigation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    navigated: list[str] = []

    def fake_to(target: str, *_args: Any, **_kwargs: Any) -> None:
        navigated.append(target)

    monkeypatch.setattr(ui.navigate, "to", fake_to)
    el = _NavElement("a")
    apply_navigation(el, "https://example.com", True, None)
    assert el._props.get("href") == "https://example.com"
    assert el._props.get("target") == "_blank"
    assert el._handlers == []
    assert navigated == []

    clicked: list[int] = []
    with_click = _NavElement("a")
    apply_navigation(with_click, "http://example.com", None, lambda: clicked.append(1))
    assert with_click._props.get("href") == "http://example.com"
    for _event, handler in with_click._handlers:
        handler()
    assert clicked == [1]
    assert navigated == []
