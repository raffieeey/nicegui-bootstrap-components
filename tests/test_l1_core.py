"""L1 pure-Python tests: dual-surface identity, aliases, grid, style, unsupported props."""

from __future__ import annotations

import contextlib
import warnings
from typing import Any

import pytest

from nicegui_bootstrap_components import bs, dbc
from nicegui_bootstrap_components._base import (
    UnsupportedPropError,
    _normalize_children,
    make_surface_classes,
    normalize_style,
    prepare_shared_props,
    resolve_class_name,
)
from nicegui_bootstrap_components.assets import StyleMode, _unscoped_payload, setup
from nicegui_bootstrap_components.bs._actions import button_dom_attrs, button_structural_classes
from nicegui_bootstrap_components.bs._layout import col_breakpoint_classes, container_class


@pytest.fixture(autouse=True)
def _reset_library_state() -> None:
    from nicegui_bootstrap_components._base import _reset_process_warnings
    from nicegui_bootstrap_components.assets import _reset_setup

    _reset_process_warnings()
    _reset_setup()
    yield
    _reset_process_warnings()
    _reset_setup()


def test_bs_button_is_not_dbc_button() -> None:
    assert bs.Button is not dbc.Button
    assert bs.button is bs.Button
    assert bs.Button.component_name == "Button"
    assert dbc.Button.component_name == "Button"
    assert not issubclass(dbc.Button, bs.Button)
    assert not issubclass(bs.Button, dbc.Button)


def test_make_surface_classes_siblings() -> None:
    class _DummyImpl:
        component_name = "Dummy"

        def __init__(self, children: object = None, *, _surface: str, **props: Any) -> None:
            self._surface = _surface
            self.children = children
            self.props = props

    native_ns: dict[str, Any] = {"_DummyImpl": _DummyImpl}
    compat_ns: dict[str, Any] = {}
    native_cls, compat_cls = make_surface_classes("Dummy", native_ns, compat_ns)
    assert native_cls is not compat_cls
    assert native_ns["Dummy"] is native_cls
    assert native_ns["dummy"] is native_cls
    assert native_ns["DbcDummy"] is compat_cls
    assert compat_ns["Dummy"] is compat_cls
    native_obj = native_cls()
    compat_obj = compat_cls()
    assert native_obj._surface == "native"
    assert compat_obj._surface == "compat"
    assert not isinstance(compat_obj, native_cls)
    assert not isinstance(native_obj, compat_cls)
    assert isinstance(compat_obj, _DummyImpl)
    assert native_cls.component_name == "Dummy"


def test_class_name_wins_over_className() -> None:
    assert resolve_class_name("a", "b", "compat") == "a"
    assert resolve_class_name("bar", None, "native") == "bar"
    assert resolve_class_name(None, "foo", "native") == "foo"


def test_className_warning_only_on_native_when_unequal() -> None:
    with pytest.warns(DeprecationWarning):
        assert resolve_class_name("a", "b", "native") == "a"
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        assert resolve_class_name("a", "b", "compat") == "a"
        assert resolve_class_name("same", "same", "native") == "same"
        assert resolve_class_name(None, "only", "native") == "only"


def test_native_className_warning_on_construct() -> None:
    with pytest.warns(DeprecationWarning), contextlib.suppress(RuntimeError):
        bs.Button("Save", class_name="a", className="b")


def test_style_dict_pxification() -> None:
    assert normalize_style({"width": 100})["width"] == "100px"
    assert normalize_style({"opacity": 0.5})["opacity"] == "0.5"
    assert normalize_style({"z-index": 5})["z-index"] == "5"
    assert normalize_style({"flex": 1})["flex"] == "1"
    assert normalize_style({"font-weight": 700})["font-weight"] == "700"
    assert normalize_style({"line-height": 1.5})["line-height"] == "1.5"
    assert normalize_style({"order": 2})["order"] == "2"
    assert normalize_style({"height": 10})["height"] == "10px"
    assert normalize_style({"width": "100%"})["width"] == "100%"
    assert normalize_style({"zIndex": 3})["zIndex"] == "3"


def test_key_rejected_on_compat_warned_on_native() -> None:
    with pytest.raises(UnsupportedPropError):
        prepare_shared_props("compat", {"key": "x"})
    props: dict[str, Any] = {"key": "x"}
    with pytest.warns(UserWarning):
        prepare_shared_props("native", props)
    assert "key" not in props


def test_col_dicts_copied_not_mutated() -> None:
    payload = {"size": 4, "offset": 2}
    snapshot = dict(payload)
    classes = col_breakpoint_classes(xs=12, md=6, xl=payload)
    assert payload == snapshot
    assert "col-12" in classes
    assert "col-md-6" in classes
    assert "col-xl-4" in classes
    assert "offset-xl-2" in classes


def test_col_xs_overrides_width() -> None:
    classes = col_breakpoint_classes(width=6, xs=12)
    assert "col-12" in classes
    assert "col-6" not in classes


def test_col_rejects_float_width() -> None:
    with pytest.raises(TypeError):
        col_breakpoint_classes(width=0.5)
    with pytest.raises(TypeError):
        bs.Col(width=0.5)


def test_col_width_fraction_string() -> None:
    classes = col_breakpoint_classes(width="1/2")
    assert "col-6" in classes


def test_col_width_true_plus_md() -> None:
    classes = col_breakpoint_classes(width=True, md=6)
    assert "col" in classes
    assert "col-md-6" in classes


def test_button_external_link_not_leaked_without_href() -> None:
    tag, attrs = button_dom_attrs(href=None, external_link=True, disabled=False)
    assert tag == "button"
    assert "href" not in attrs
    assert "external_link" not in attrs
    assert "target" not in attrs
    tag, attrs = button_dom_attrs(href="/x", external_link=True, disabled=False)
    assert tag == "a"
    assert attrs["href"] == "/x"
    assert attrs["target"] == "_blank"
    assert "external_link" not in attrs
    tag, attrs = button_dom_attrs(href=None, external_link=False, disabled=False)
    assert "external_link" not in attrs


def test_button_structural_classes() -> None:
    assert "btn-primary" in button_structural_classes(color="primary")
    assert "btn-outline-secondary" in button_structural_classes(color="secondary", outline=True)
    assert "btn-link" in button_structural_classes(color="link")
    with pytest.raises(ValueError):
        button_structural_classes(color="not-a-color")
    with pytest.raises(ValueError):
        bs.Button(color="not-a-color")


def test_compat_container_rejects_string_fluid() -> None:
    with pytest.raises(UnsupportedPropError):
        container_class("sm", surface="compat")
    with pytest.raises(UnsupportedPropError):
        dbc.Container(fluid="sm")
    assert container_class("sm", surface="native") == "container-sm"


def test_normalize_children_flatten() -> None:
    assert _normalize_children(None) == []
    assert _normalize_children("x") == ["x"]
    assert _normalize_children([1, None, ["a", (2, None)]]) == [1, "a", 2]
    with pytest.raises(TypeError):
        _normalize_children(True)
    with pytest.raises(TypeError):
        _normalize_children(object())


def test_setup_idempotent_and_conflict(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui_bootstrap_components import assets

    monkeypatch.setattr(assets, "add_head_html", lambda *_a, **_k: None)
    monkeypatch.setattr(assets, "add_static_files", lambda *_a, **_k: None)
    setup(mode=StyleMode.MIXED)
    setup(mode=StyleMode.MIXED)
    with pytest.raises(ValueError):
        setup(mode=StyleMode.UNSCOPED)


def test_unscoped_payload_preserves_hyphenated_scope_names() -> None:
    sample = (
        ".ngbs { color: red; } .ngbs .btn { color: blue; } "
        ".ngbs-overlay { z-index: 1; } "
        '.ngbs[data-bs-theme="dark"] { color: white; } .ngbs * { box-sizing: border-box; }'
    )
    transformed = _unscoped_payload(sample)
    assert ":root { color: red; }" in transformed
    assert ".btn { color: blue; }" in transformed
    assert ".ngbs-overlay" in transformed
    assert ':root[data-bs-theme="dark"]' not in transformed
    assert '[data-bs-theme="dark"]' in transformed
    assert "* { box-sizing: border-box; }" in transformed
    assert ":root-overlay" not in transformed


def test_dbc_input_rejects_color_and_int_debounce() -> None:
    if not hasattr(dbc, "Input"):
        pytest.skip("Input not available")
    with pytest.raises(UnsupportedPropError):
        dbc.Input(type="color")
    with pytest.raises(UnsupportedPropError):
        dbc.Input(debounce=250)


def test_native_input_allows_color_and_int_debounce() -> None:
    if not hasattr(bs, "Input") and not hasattr(bs, "input"):
        pytest.skip("Input not available")
    factory = getattr(bs, "input", bs.Input)
    try:
        factory(type="color")
    except UnsupportedPropError:
        raise
    except Exception:
        pass
    try:
        factory(debounce=250)
    except UnsupportedPropError:
        raise
    except Exception:
        pass


def test_dbc_dropdown_rejects_is_open_native_allows() -> None:
    if not hasattr(dbc, "DropdownMenu"):
        pytest.skip("DropdownMenu not available")
    with pytest.raises(UnsupportedPropError):
        dbc.DropdownMenu(is_open=True)
    if not hasattr(bs, "DropdownMenu"):
        pytest.skip("native DropdownMenu not available")
    try:
        bs.DropdownMenu(is_open=True)
    except UnsupportedPropError:
        raise
    except Exception:
        pass
