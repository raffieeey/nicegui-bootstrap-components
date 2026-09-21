"""Alert and Spinner family (native + compat sibling types)."""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any

from nicegui import ui

from .._base import (
    BootstrapElement,
    make_surface_classes,
    normalize_style,
    resolve_class_name,
)
from .._host import set_element_text
from ._overlays import _adopt_into, _ensure_overlay_runtime, _portal_to_overlay_root

__all__ = [
    "Alert",
    "DbcAlert",
    "alert",
    "Spinner",
    "DbcSpinner",
    "spinner",
    "alert_structural_classes",
    "spinner_structural_classes",
    "spinner_color_css",
    "spinner_is_visible",
    "spinner_fullscreen_classes",
]

_SEMANTIC_COLORS: tuple[str, ...] = (
    "primary",
    "secondary",
    "success",
    "danger",
    "warning",
    "info",
    "light",
    "dark",
)
_SPINNER_TYPES: tuple[str, ...] = ("border", "grow")
_SPINNER_SIZES: tuple[str, ...] = ("sm",)
_SPINNER_DISPLAYS: tuple[str, ...] = ("auto", "show", "hide")


def alert_structural_classes(
    *,
    color: str,
    dismissable: bool = False,
    fade: bool = True,
    is_open: bool = True,
) -> list[str]:
    """Return Bootstrap ``alert`` classes. Unknown colors raise ``ValueError``."""
    if color not in _SEMANTIC_COLORS:
        raise ValueError(f"Unknown Alert color {color!r}")
    classes = ["alert", f"alert-{color}"]
    if dismissable:
        classes.append("alert-dismissible")
    if fade:
        classes.append("fade")
        if is_open:
            classes.append("show")
    elif not is_open:
        classes.append("d-none")
    return classes


def spinner_structural_classes(
    *,
    type: str = "border",
    size: str | None = None,
    color: str | None = None,
) -> list[str]:
    """Return Bootstrap spinner classes. Unknown type or size raise ``ValueError``."""
    if type not in _SPINNER_TYPES:
        raise ValueError(f"Unknown Spinner type {type!r}; expected 'border' or 'grow'")
    if size is not None and size not in _SPINNER_SIZES:
        raise ValueError(f"Unknown Spinner size {size!r}; expected 'sm' or None")
    classes = [f"spinner-{type}"]
    if size is not None:
        classes.append(f"spinner-{type}-{size}")
    if color is not None and color in _SEMANTIC_COLORS:
        classes.append(f"text-{color}")
    return classes


def spinner_color_css(color: str | None) -> str | None:
    """Return an inline CSS color for arbitrary (non-semantic) spinner colors."""
    if color is None or color in _SEMANTIC_COLORS:
        return None
    return color


def spinner_is_visible(
    *,
    display: str = "auto",
    loading: bool | None = None,
    has_children: bool = False,
    fullscreen: bool = False,
) -> bool:
    """Return whether the spinner graphic should be shown."""
    if display not in _SPINNER_DISPLAYS:
        raise ValueError(f"Unknown Spinner display {display!r}; expected 'auto', 'show', or 'hide'")
    if display == "hide":
        return False
    if display == "show":
        return True
    if loading is not None:
        return bool(loading)
    if fullscreen:
        return True
    return not has_children


def spinner_fullscreen_classes() -> list[str]:
    """Return classes for a fullscreen spinner overlay root."""
    return [
        "position-fixed",
        "top-0",
        "start-0",
        "w-100",
        "h-100",
        "d-flex",
        "align-items-center",
        "justify-content-center",
    ]


def _spinner_node_css(
    *,
    color: str | None,
    spinner_style: dict[str, Any] | None,
) -> str | None:
    parts: list[str] = []
    extra = spinner_color_css(color)
    if extra is not None:
        parts.append(f"color: {extra}")
    if spinner_style:
        css_val: Any = normalize_style(spinner_style)
        if isinstance(css_val, dict):
            css_val = "; ".join(f"{key}: {value}" for key, value in css_val.items())
        text = str(css_val).strip().rstrip(";")
        if text:
            parts.append(text)
    if not parts:
        return None
    return "; ".join(parts)


def _mount_spinner_label() -> None:
    label = ui.element("span").classes("visually-hidden")
    setter = getattr(label, "set_text", None)
    if callable(setter):
        setter("Loading...")
    else:
        set_element_text(label, "Loading...")


def _deactivate_timer(timer: Any) -> None:
    with contextlib.suppress(Exception):
        timer.deactivate()


def _attach_passed_children(host: Any, children: object) -> None:
    """Place constructor children onto ``host`` without using ``children=`` on init."""
    if children is None:
        return
    if isinstance(children, str):
        setter = getattr(host, "set_text", None)
        if callable(setter):
            setter(children)
        else:
            set_element_text(host, children)
        return
    _adopt_into(host, children)


class _AlertImpl(BootstrapElement):
    """Private Alert implementation."""

    component_name = "Alert"
    children_kind = "auto"
    reserved_classes = ("alert",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        color: str = "primary",
        dismissable: bool = False,
        fade: bool = True,
        is_open: bool = True,
        duration: int | None = None,
        on_dismiss: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        if duration is not None:
            duration_ms = int(duration)
            if duration_ms < 0:
                raise ValueError("Alert duration must be None or a non-negative integer")
            self._duration: int | None = duration_ms
        else:
            self._duration = None
        self._structural_classes = tuple(
            alert_structural_classes(
                color=color,
                dismissable=bool(dismissable),
                fade=bool(fade),
                is_open=bool(is_open),
            )
        )
        self._is_open = bool(is_open)
        self._fade = bool(fade)
        self._on_dismiss = on_dismiss
        self._timer: Any | None = None
        super().__init__(None, tag="div", **kwargs)
        self._props["role"] = "alert"
        _attach_passed_children(self, children)
        if dismissable:
            with self:
                close = ui.element("button").classes("btn-close")
                close._props["type"] = "button"
                close._props["aria-label"] = "Close"
                close.on("click", self._handle_dismiss)
        self._arm_duration_timer()

    @property
    def is_open(self) -> bool:
        return self._is_open

    @is_open.setter
    def is_open(self, value: bool) -> None:
        wanted = bool(value)
        if wanted == self._is_open:
            return
        if wanted:
            self._is_open = True
            self._apply_open_classes()
            self._arm_duration_timer()
        else:
            self._handle_dismiss()

    def _apply_open_classes(self) -> None:
        if self._is_open:
            if self._fade:
                self.classes(add="show", remove="d-none")
            else:
                self.classes(remove="d-none")
        elif self._fade:
            self.classes(remove="show")
        else:
            self.classes(add="d-none")

    def _cancel_timer(self) -> None:
        timer = self._timer
        self._timer = None
        if timer is not None:
            _deactivate_timer(timer)

    def _arm_duration_timer(self) -> None:
        self._cancel_timer()
        if self._duration is not None and self._duration > 0 and self._is_open:
            self._timer = ui.timer(
                self._duration / 1000.0,
                self._handle_dismiss,
                once=True,
            )

    def _handle_dismiss(self, *_args: Any, **_kwargs: Any) -> None:
        if not self._is_open:
            return
        self._is_open = False
        self._cancel_timer()
        self._apply_open_classes()
        if self._on_dismiss is not None:
            self._on_dismiss()

    def _handle_delete(self) -> None:
        self._cancel_timer()
        super()._handle_delete()


Alert, DbcAlert = make_surface_classes("Alert", globals())
alert = Alert


class _SpinnerImpl(BootstrapElement):
    """Private Spinner implementation."""

    component_name = "Spinner"
    children_kind = "auto"
    reserved_classes: tuple[str, ...] = ()

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        color: str | None = None,
        type: str = "border",
        size: str | None = None,
        loading: bool | None = None,
        display: str = "auto",
        delay_show: int | None = None,
        delay_hide: int | None = None,
        fullscreen: bool = False,
        spinner_style: dict[str, Any] | None = None,
        spinner_class_name: str | None = None,
        spinnerClassName: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        spinner_classes = spinner_structural_classes(type=type, size=size, color=color)
        has_children = children is not None
        visible = spinner_is_visible(
            display=display,
            loading=loading,
            has_children=has_children,
            fullscreen=bool(fullscreen),
        )
        if delay_show is not None:
            delay_show_ms = int(delay_show)
            if delay_show_ms < 0:
                raise ValueError("Spinner delay_show must be None or a non-negative integer")
            self._delay_show: int | None = delay_show_ms
        else:
            self._delay_show = None
        if delay_hide is not None:
            delay_hide_ms = int(delay_hide)
            if delay_hide_ms < 0:
                raise ValueError("Spinner delay_hide must be None or a non-negative integer")
            self._delay_hide: int | None = delay_hide_ms
        else:
            self._delay_hide = None
        use_wrapper = has_children or bool(fullscreen)
        if use_wrapper:
            wrapper = spinner_fullscreen_classes() if fullscreen else []
            self._structural_classes = tuple(wrapper)
        else:
            classes = list(spinner_classes)
            if not visible:
                classes.append("d-none")
            self._structural_classes = tuple(classes)
        self._fullscreen = bool(fullscreen)
        self._delay_timers: list[Any] = []
        if fullscreen:
            _ensure_overlay_runtime()
        super().__init__(None, tag="div", **kwargs)
        resolved_cn: str | None = None
        if spinner_class_name is not None or spinnerClassName is not None:
            resolved_cn = resolve_class_name(spinner_class_name, spinnerClassName, self._surface)
        inline = _spinner_node_css(color=color, spinner_style=spinner_style)
        if use_wrapper:
            _attach_passed_children(self, children)
            with self:
                spinner_el = ui.element("div")
                spinner_el.classes(" ".join(spinner_classes))
                if resolved_cn:
                    spinner_el.classes(resolved_cn)
                if not visible:
                    spinner_el.classes(add="d-none")
                spinner_el._props["role"] = "status"
                if inline:
                    spinner_el._props["style"] = inline
                with spinner_el:
                    _mount_spinner_label()
            self._spinner_el: Any = spinner_el
        else:
            self._spinner_el = self
            self._props["role"] = "status"
            if resolved_cn:
                self.classes(resolved_cn)
            if inline:
                existing = self._props.get("style")
                if existing:
                    self._props["style"] = f"{existing}; {inline}"
                else:
                    self._props["style"] = inline
            with self:
                _mount_spinner_label()
        if visible and self._delay_show is not None and self._delay_show > 0:
            self._set_spinner_visible(False)
            self._delay_timers.append(
                ui.timer(self._delay_show / 1000.0, self._show_spinner, once=True)
            )
        elif (not visible) and self._delay_hide is not None and self._delay_hide > 0:
            self._set_spinner_visible(True)
            self._delay_timers.append(
                ui.timer(self._delay_hide / 1000.0, self._hide_spinner, once=True)
            )
        if fullscreen:
            _portal_to_overlay_root(self)

    def _set_spinner_visible(self, visible: bool) -> None:
        if visible:
            self._spinner_el.classes(remove="d-none")
        else:
            self._spinner_el.classes(add="d-none")

    def _show_spinner(self) -> None:
        self._set_spinner_visible(True)

    def _hide_spinner(self) -> None:
        self._set_spinner_visible(False)

    def _clear_delay_timers(self) -> None:
        timers = self._delay_timers
        self._delay_timers = []
        for timer in timers:
            _deactivate_timer(timer)

    def _handle_delete(self) -> None:
        self._clear_delay_timers()
        super()._handle_delete()


Spinner, DbcSpinner = make_surface_classes("Spinner", globals())
spinner = Spinner
