"""Toast component with overlay portal support."""

from __future__ import annotations

import contextlib
from collections.abc import Callable
from typing import Any

from nicegui import ui

from .._base import BootstrapElement
from .._host import set_element_text
from ._overlays import (
    _adopt_into,
    _bind_kind,
    _ensure_overlay_runtime,
    _make_surfaces,
    _OpenMixin,
    _portal_to_overlay_root,
    _SlotRedirect,
    _surface_of,
    _wire_overlay_events,
)


def toast_structural_classes(*, is_open: bool = True) -> list[str]:
    """Return Bootstrap ``toast`` classes."""
    classes = ["toast"]
    if is_open:
        classes.append("show")
    return classes


class _ToastImpl(_SlotRedirect, _OpenMixin, BootstrapElement):
    component_name = "Toast"
    styling_target = "root"
    reserved_classes = ("toast", "show")
    _css_show = True

    def __init__(
        self,
        children: Any = None,
        *,
        _surface: str | None = None,
        is_open: bool = True,
        header: str | None = None,
        icon: str | None = None,
        dismissable: bool = False,
        duration: int | None = None,
        delay: int | None = None,
        on_dismiss: Callable[..., Any] | None = None,
        class_name: str | None = None,
        header_class_name: str | None = None,
        body_class_name: str | None = None,
        style: dict[str, Any] | None = None,
        id: str | None = None,
        className: str | None = None,
        key: Any = None,
        on_show: Callable[..., Any] | None = None,
        on_shown: Callable[..., Any] | None = None,
        on_hide: Callable[..., Any] | None = None,
        on_hidden: Callable[..., Any] | None = None,
    ) -> None:
        surface = _surface_of(self, _surface)
        with contextlib.suppress(Exception):
            self._surface = surface
        if duration is None and delay is not None:
            duration = delay
        _ensure_overlay_runtime()
        self._structural_classes = tuple(toast_structural_classes(is_open=bool(is_open)))
        super().__init__(
            children=None,
            id=id,
            class_name=class_name,
            className=className,
            style=style,
            key=key,
        )
        self._surface = surface
        self.classes("toast")
        self._props["role"] = "alert"
        self._props["aria-live"] = "polite"
        self._props["aria-atomic"] = "true"
        with self:
            if header is not None or icon is not None or dismissable:
                header_classes = ["toast-header"]
                if header_class_name:
                    header_classes.append(header_class_name)
                header_el = ui.element("div").classes(" ".join(header_classes))
                with header_el:
                    if icon:
                        ic = ui.element("span").classes(str(icon))
                        _ = ic
                    if header is not None:
                        strong = ui.element("strong").classes("me-auto")
                        if hasattr(strong, "set_text"):
                            strong.set_text(str(header))
                        else:
                            set_element_text(strong, str(header))
                    if dismissable:
                        close = ui.element("button").classes("btn-close")
                        close._props["type"] = "button"
                        close._props["data-ngbs-dismiss"] = "toast"
            body_classes = ["toast-body"]
            if body_class_name:
                body_classes.append(body_class_name)
            self._slot_host = ui.element("div").classes(" ".join(body_classes))
        self._children_passed = children is not None
        if children is not None:
            _adopt_into(self._slot_host, children, owner=self)
        self._apply_open(bool(is_open))
        _bind_kind(
            self,
            "toast",
            open=bool(is_open),
            duration=duration,
            dismissable=bool(dismissable),
        )
        _portal_to_overlay_root(self)
        _wire_overlay_events(
            self,
            on_show=on_show,
            on_shown=on_shown,
            on_hide=on_hide,
            on_hidden=on_hidden,
            on_dismiss=on_dismiss,
        )

    def _handle_delete(self) -> None:
        self._props["data-ngbs-open"] = "false"
        super()._handle_delete()


Toast, DbcToast = _make_surfaces(_ToastImpl)
toast = Toast

__all__ = ["Toast", "DbcToast", "toast", "toast_structural_classes"]
