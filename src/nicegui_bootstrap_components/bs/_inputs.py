"""Input and Textarea controls with Bootstrap form-control styling."""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any

from nicegui import ui

from .._base import (
    BootstrapValueElement,
    PropConflictError,
    UnsupportedPropError,
    make_surface_classes,
)

_UNSET = object()

COMPAT_INPUT_TYPES = frozenset(
    {"text", "number", "password", "email", "range", "search", "tel", "url", "hidden", "time"}
)
NATIVE_INPUT_TYPES = COMPAT_INPUT_TYPES | {"color"}

_JS_INPUT = """(e) => {
  const root = e.currentTarget || e.target;
  let input = e.target;
  if (!input || (input.tagName !== 'INPUT' && input.tagName !== 'TEXTAREA')) {
    input = root && root.querySelector ? root.querySelector('input,textarea') : input;
  }
  if (!input) return;
  if (e.isComposing) return;
  const mode = input.getAttribute('data-ngbs-debounce')
    || (root && root.getAttribute && root.getAttribute('data-ngbs-debounce'))
    || 'false';
  const send = () => emit(input.value == null ? '' : String(input.value));
  if (mode === 'false') { send(); return; }
  if (mode === 'true') { return; }
  const ms = Number(mode);
  if (!Number.isFinite(ms) || ms < 0) { send(); return; }
  if (input._ngbsDebounceTimer) clearTimeout(input._ngbsDebounceTimer);
  input._ngbsDebounceTimer = setTimeout(() => {
    input._ngbsDebounceTimer = null;
    emit(input.value == null ? '' : String(input.value));
  }, ms);
}"""

_JS_BLUR = """(e) => {
  const root = e.currentTarget || e.target;
  let input = e.target;
  if (!input || (input.tagName !== 'INPUT' && input.tagName !== 'TEXTAREA')) {
    input = root && root.querySelector ? root.querySelector('input,textarea') : input;
  }
  if (!input) return;
  if (input._ngbsDebounceTimer) {
    clearTimeout(input._ngbsDebounceTimer);
    input._ngbsDebounceTimer = null;
  }
  emit(input.value == null ? '' : String(input.value));
}"""

_JS_ENTER = """(e) => {
  const root = e.currentTarget || e.target;
  let input = e.target;
  if (!input || (input.tagName !== 'INPUT' && input.tagName !== 'TEXTAREA')) {
    input = root && root.querySelector ? root.querySelector('input,textarea') : input;
  }
  if (!input) return;
  if (e.isComposing || e.key !== 'Enter') return;
  if (input.tagName === 'TEXTAREA') return;
  if (input._ngbsDebounceTimer) {
    clearTimeout(input._ngbsDebounceTimer);
    input._ngbsDebounceTimer = null;
  }
  emit(input.value == null ? '' : String(input.value));
}"""


def _make_surfaces(impl_cls: type) -> tuple[type, type]:
    name = getattr(impl_cls, "component_name", None) or impl_cls.__name__
    if name.startswith("_"):
        name = name[1:]
    if name.endswith("Impl"):
        name = name[:-4]
    attempts = (
        lambda: make_surface_classes(impl_cls, component_name=name),
        lambda: make_surface_classes(impl_cls),
    )
    for attempt in attempts:
        try:
            result = attempt()
        except TypeError:
            continue
        if isinstance(result, (tuple, list)) and len(result) >= 2:
            return result[0], result[1]

    def _wrap(surface: str, cls_name: str) -> type:
        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            kwargs.setdefault("_surface", surface)
            impl_cls.__init__(self, *args, **kwargs)

        return type(
            cls_name,
            (impl_cls,),
            {
                "_surface": surface,
                "component_name": getattr(impl_cls, "component_name", name),
                "__init__": __init__,
                "__module__": impl_cls.__module__,
            },
        )

    return _wrap("native", name), _wrap("compat", f"Dbc{name}")


def _surface_of(el: Any, explicit: str | None) -> str:
    if explicit in {"native", "compat"}:
        return explicit
    value = getattr(el, "_surface", None) or getattr(type(el), "_surface", None)
    return value if value in {"native", "compat"} else "native"


def _payload(e: Any) -> Any:
    args = getattr(e, "args", e)
    if isinstance(args, dict) and "value" in args:
        return args["value"]
    if isinstance(args, (list, tuple)):
        if not args:
            return ""
        first = args[0]
        if isinstance(first, dict) and "value" in first:
            return first["value"]
        return first
    return args


def _validate_type(surface: str, type_: str) -> str:
    if type_ == "color" and surface == "compat":
        raise UnsupportedPropError("type='color' is a native-only Input extension")
    allowed = NATIVE_INPUT_TYPES if surface == "native" else COMPAT_INPUT_TYPES
    if type_ not in allowed:
        raise UnsupportedPropError(f"Unsupported Input type={type_!r} on {surface} surface")
    return type_


def _validate_debounce(surface: str, debounce: bool | int) -> bool | int:
    if isinstance(debounce, bool):
        return debounce
    if isinstance(debounce, int):
        if surface == "compat":
            raise UnsupportedPropError("integer debounce is a native-only Input/Textarea extension")
        if debounce < 0:
            raise ValueError("debounce milliseconds must be >= 0")
        return int(debounce)
    raise TypeError(f"debounce must be bool or int, got {type(debounce)!r}")


def _debounce_attr(debounce: bool | int) -> str:
    if debounce is False:
        return "false"
    if debounce is True:
        return "true"
    return str(int(debounce))


def _set_attr(el: Any, name: str, value: Any) -> None:
    if value is None:
        return
    el._props[name] = value


class _TextControlBase(BootstrapValueElement):
    """Shared value publishing for Input/Textarea. Root tag must be the native control."""

    component_name = "Input"
    styling_target = "root"
    reserved_classes: tuple[str, ...] = (
        "form-control",
        "form-control-sm",
        "form-control-lg",
        "form-control-plaintext",
        "form-range",
        "is-valid",
        "is-invalid",
    )

    def _configure_control(
        self,
        *,
        tag: str,
        type_: str | None,
        placeholder: str | None,
        size: str | None,
        plaintext: bool,
        disabled: bool,
        readonly: bool,
        debounce: bool | int,
        valid: bool | None,
        invalid: bool | None,
        min_value: Any,
        max_value: Any,
        step: Any,
        maxlength: int | None,
        autocomplete: str | None,
        name: str | None,
        list_id: str | None,
        pattern: str | None,
        required: bool,
        html_size: int | None,
        rows: int | None,
        allow_submit: bool,
        n_submit: int,
        n_blur: int,
        on_submit: Callable[..., Any] | None,
        on_blur: Callable[..., Any] | None,
    ) -> None:
        self.n_submit = int(n_submit)
        self.n_blur = int(n_blur)
        self._on_submit_cb = on_submit
        self._on_blur_cb = on_blur
        self._allow_submit = allow_submit
        self._debounce = debounce

        with contextlib.suppress(Exception):
            self._surface = _surface_of(self, getattr(self, "_surface", None))

        if tag == "input" and type_:
            _set_attr(self, "type", type_)
        if placeholder is not None:
            _set_attr(self, "placeholder", placeholder)
        if html_size is not None:
            _set_attr(self, "size", int(html_size))
        if rows is not None:
            _set_attr(self, "rows", int(rows))
        if min_value is not None:
            _set_attr(self, "min", min_value)
        if max_value is not None:
            _set_attr(self, "max", max_value)
        if step is not None:
            _set_attr(self, "step", step)
        if maxlength is not None:
            _set_attr(self, "maxlength", int(maxlength))
        if autocomplete is not None:
            _set_attr(self, "autocomplete", autocomplete)
        if name is not None:
            _set_attr(self, "name", name)
        if list_id is not None:
            _set_attr(self, "list", list_id)
        if pattern is not None:
            _set_attr(self, "pattern", pattern)
        if required:
            _set_attr(self, "required", True)
        if disabled:
            _set_attr(self, "disabled", True)
            if hasattr(self, "disable"):
                with contextlib.suppress(Exception):
                    self.disable()
        if readonly:
            _set_attr(self, "readonly", True)

        _set_attr(self, "data-ngbs-debounce", _debounce_attr(debounce))
        _set_attr(self, "data-ngbs-component", self.component_name)
        with contextlib.suppress(Exception):
            _set_attr(self, "data-ngbs-eid", str(self.id))

        self._apply_form_classes(
            type_=type_, size=size, plaintext=plaintext, valid=valid, invalid=invalid
        )
        self._sync_value_attr(getattr(self, "value", ""))

        self.on("input", self._on_input, js_handler=_JS_INPUT)
        self.on("compositionend", self._on_input, js_handler=_JS_INPUT)
        self.on("blur", self._on_blur, js_handler=_JS_BLUR)
        if allow_submit:
            self.on("keydown", self._on_enter, js_handler=_JS_ENTER)

    def _apply_form_classes(
        self,
        *,
        type_: str | None,
        size: str | None,
        plaintext: bool,
        valid: bool | None,
        invalid: bool | None,
    ) -> None:
        if type_ == "hidden":
            return
        classes: list[str] = []
        if type_ == "range":
            classes.append("form-range")
        elif plaintext:
            classes.append("form-control-plaintext")
        else:
            classes.append("form-control")
        if size in {"sm", "lg"} and type_ != "range" and not plaintext:
            classes.append(f"form-control-{size}")
        elif size in {"sm", "lg"} and type_ == "range":
            classes.append(f"form-range-{size}")
        if valid:
            classes.append("is-valid")
        if invalid:
            classes.append("is-invalid")
        if classes:
            self.classes(" ".join(classes))

    def _sync_value_attr(self, value: Any) -> None:
        text = "" if value is None else str(value)
        self._props["value"] = text
        self._props["model-value"] = text

    def _publish(self, e: Any) -> None:
        raw = _payload(e)
        if raw is None:
            raw = ""
        try:
            current = self.value
        except Exception:
            current = None
        if current is None:
            current = ""
        if str(raw) == str(current):
            self._sync_value_attr(raw)
            return
        if hasattr(self, "set_value"):
            self.set_value(raw)
        else:
            self.value = raw
        self._sync_value_attr(raw)

    def _on_input(self, e: Any) -> None:
        self._publish(e)

    def _on_blur(self, e: Any) -> None:
        self.n_blur = int(getattr(self, "n_blur", 0)) + 1
        self._publish(e)
        if self._on_blur_cb is not None:
            self._on_blur_cb(getattr(self, "value", ""))

    def _on_enter(self, e: Any) -> None:
        self.n_submit = int(getattr(self, "n_submit", 0)) + 1
        self._publish(e)
        if self._on_submit_cb is not None:
            self._on_submit_cb(getattr(self, "value", ""))


class _InputImpl(_TextControlBase):
    component_name = "Input"

    def __init__(
        self,
        value: str | float | None = "",
        *,
        _surface: str | None = None,
        type: str = "text",
        placeholder: str | None = None,
        size: str | None = None,
        plaintext: bool = False,
        disabled: bool = False,
        readonly: bool = False,
        read_only: bool | None = None,
        debounce: bool | int = False,
        n_submit: int = 0,
        n_blur: int = 0,
        valid: bool | None = None,
        invalid: bool | None = None,
        min: Any = None,
        max: Any = None,
        step: Any = None,
        maxlength: int | None = None,
        autocomplete: str | None = None,
        name: str | None = None,
        list: str | None = None,
        pattern: str | None = None,
        required: bool = False,
        persist: str = "off",
        on_change: Callable[..., Any] | None = None,
        on_submit: Callable[..., Any] | None = None,
        on_blur: Callable[..., Any] | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        html_size: int | None = None,
        key: Any = None,
        children: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        type_ = _validate_type(surface, type)
        debounce = _validate_debounce(surface, debounce)
        if read_only is not None:
            if surface == "compat":
                raise UnsupportedPropError("read_only is a native alias of readonly")
            readonly = bool(read_only)
        if valid and invalid:
            raise PropConflictError("valid and invalid cannot both be True")
        if persist not in {"off", "local", "session"}:
            raise ValueError("persist must be 'off', 'local', or 'session'")
        if persist != "off" and not id:
            raise ValueError("persist requires a public id")
        if value is None:
            value = ""
        super().__init__(
            children=children,
            value=value,
            on_change=on_change,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            tag="input",
            key=key,
        )
        self._surface = surface
        self._configure_control(
            tag="input",
            type_=type_,
            placeholder=placeholder,
            size=size,
            plaintext=plaintext,
            disabled=disabled,
            readonly=readonly,
            debounce=debounce,
            valid=valid,
            invalid=invalid,
            min_value=min,
            max_value=max,
            step=step,
            maxlength=maxlength,
            autocomplete=autocomplete,
            name=name,
            list_id=list,
            pattern=pattern,
            required=required,
            html_size=html_size,
            rows=None,
            allow_submit=True,
            n_submit=n_submit,
            n_blur=n_blur,
            on_submit=on_submit,
            on_blur=on_blur,
        )


class _TextareaImpl(_TextControlBase):
    component_name = "Textarea"
    reserved_classes = (
        "form-control",
        "form-control-sm",
        "form-control-lg",
        "form-control-plaintext",
        "is-valid",
        "is-invalid",
    )

    def __init__(
        self,
        value: str | None = "",
        *,
        _surface: str | None = None,
        placeholder: str | None = None,
        size: str | None = None,
        plaintext: bool = False,
        disabled: bool = False,
        readonly: bool = False,
        read_only: bool | None = None,
        debounce: bool | int = False,
        n_blur: int = 0,
        valid: bool | None = None,
        invalid: bool | None = None,
        maxlength: int | None = None,
        autocomplete: str | None = None,
        name: str | None = None,
        required: bool = False,
        persist: str = "off",
        rows: int | None = None,
        on_change: Callable[..., Any] | None = None,
        on_blur: Callable[..., Any] | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        key: Any = None,
        children: Any = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        debounce = _validate_debounce(surface, debounce)
        if read_only is not None:
            if surface == "compat":
                raise UnsupportedPropError("read_only is a native alias of readonly")
            readonly = bool(read_only)
        if valid and invalid:
            raise PropConflictError("valid and invalid cannot both be True")
        if persist not in {"off", "local", "session"}:
            raise ValueError("persist must be 'off', 'local', or 'session'")
        if persist != "off" and not id:
            raise ValueError("persist requires a public id")
        if value is None:
            value = ""
        super().__init__(
            children=children,
            value=value,
            on_change=on_change,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            tag="textarea",
            key=key,
        )
        self._surface = surface
        self._configure_control(
            tag="textarea",
            type_=None,
            placeholder=placeholder,
            size=size,
            plaintext=plaintext,
            disabled=disabled,
            readonly=readonly,
            debounce=debounce,
            valid=valid,
            invalid=invalid,
            min_value=None,
            max_value=None,
            step=None,
            maxlength=maxlength,
            autocomplete=autocomplete,
            name=name,
            list_id=None,
            pattern=None,
            required=required,
            html_size=None,
            rows=rows,
            allow_submit=False,
            n_submit=0,
            n_blur=n_blur,
            on_submit=None,
            on_blur=on_blur,
        )


Input, DbcInput = _make_surfaces(_InputImpl)
Textarea, DbcTextarea = _make_surfaces(_TextareaImpl)
input = Input
textarea = Textarea

__all__ = [
    "Input",
    "DbcInput",
    "input",
    "Textarea",
    "DbcTextarea",
    "textarea",
]

# Keep ui imported so NiceGUI page context is resolved the same way as other bs modules.
_ = ui
