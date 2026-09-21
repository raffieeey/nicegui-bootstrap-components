"""Button family: Button, ButtonGroup (native + compat sibling types)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .._base import BootstrapElement, make_surface_classes

__all__ = [
    "Button",
    "ButtonGroup",
    "DbcButton",
    "DbcButtonGroup",
    "button",
    "button_dom_attrs",
    "button_group",
    "button_group_classes",
    "button_structural_classes",
]

_COLORS = frozenset(
    {
        "primary",
        "secondary",
        "success",
        "info",
        "warning",
        "danger",
        "light",
        "dark",
        "link",
    }
)
_SIZES = frozenset({"sm", "lg", "md"})
_GROUP_SIZES = frozenset({"sm", "lg", "md"})
_TYPES = frozenset({"button", "reset", "submit"})


def button_structural_classes(
    *,
    color: str,
    outline: bool = False,
    size: str | None = None,
    active: bool = False,
    disabled: bool = False,
    as_link: bool = False,
) -> list[str]:
    """Return Bootstrap ``btn`` classes. Unknown colors raise ``ValueError``."""
    if color not in _COLORS:
        raise ValueError(f"Unknown Button color: {color!r}")
    if size is not None and size not in _SIZES:
        raise ValueError(f"Invalid Button size: {size!r}")
    classes = ["btn"]
    if color == "link":
        classes.append("btn-link")
    elif outline:
        classes.append(f"btn-outline-{color}")
    else:
        classes.append(f"btn-{color}")
    if size and size != "md":
        classes.append(f"btn-{size}")
    if active:
        classes.append("active")
    if disabled and as_link:
        classes.append("disabled")
    return classes


def button_dom_attrs(
    *,
    href: str | None,
    external_link: bool | None,
    disabled: bool,
    type: str = "button",
    target: str | None = None,
    download: str | bool | None = None,
    name: str | None = None,
    value: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Return ``(tag, attrs)``. Falsy href is omitted; ``external_link`` never leaks."""
    if type not in _TYPES:
        raise ValueError(f"Invalid Button type: {type!r}")
    as_link = bool(href)
    attrs: dict[str, Any] = {}
    if as_link:
        attrs["href"] = href
        attrs["role"] = "button"
        if external_link is True:
            attrs["target"] = "_blank"
            attrs["rel"] = "noopener noreferrer"
        elif target:
            attrs["target"] = target
        if download is True:
            attrs["download"] = True
        elif download:
            attrs["download"] = download
        if disabled:
            attrs["aria-disabled"] = "true"
            attrs["tabindex"] = "-1"
    else:
        attrs["type"] = type
        if disabled:
            attrs["disabled"] = True
    if name:
        attrs["name"] = name
    if value is not None and value != "":
        attrs["value"] = value
    return ("a" if as_link else "button", attrs)


def button_group_classes(*, size: str | None = None, vertical: bool = False) -> list[str]:
    """Return Bootstrap ``btn-group`` classes."""
    if size is not None and size not in _GROUP_SIZES:
        raise ValueError(f"Invalid ButtonGroup size: {size!r}")
    classes = ["btn-group"]
    if size in {"sm", "lg"}:
        classes.append(f"btn-group-{size}")
    if vertical:
        classes.append("btn-group-vertical")
    return classes


def _apply_dom_attrs(element: Any, attrs: dict[str, Any]) -> None:
    parts: list[str] = []
    for key, val in attrs.items():
        if val is True:
            parts.append(str(key))
        elif val is False or val is None or val == "":
            continue
        else:
            parts.append(f"{key}={val}")
    if parts:
        element.props(" ".join(parts))


class _ButtonImpl(BootstrapElement):
    """Private Button implementation. Click listener is registered in ``__init__`` only."""

    component_name = "Button"
    children_kind = "phrasing"
    reserved_classes = ("btn",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        color: str = "primary",
        outline: bool = False,
        size: str | None = None,
        disabled: bool = False,
        active: bool = False,
        n_clicks: int = 0,
        type: str = "button",
        href: str | None = None,
        external_link: bool | None = None,
        download: str | bool | None = None,
        target: str | None = None,
        name: str | None = None,
        value: str | None = None,
        on_click: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        tag, attrs = button_dom_attrs(
            href=href,
            external_link=external_link,
            disabled=disabled,
            type=type,
            target=target,
            download=download,
            name=name,
            value=value,
        )
        self._structural_classes = tuple(
            button_structural_classes(
                color=color,
                outline=outline,
                size=size,
                active=active,
                disabled=disabled,
                as_link=tag == "a",
            )
        )
        self._desired_tag = tag
        self._html_attrs = attrs
        self._n_clicks = int(n_clicks)
        self.disabled = bool(disabled)
        self._on_click = on_click
        super().__init__(children, tag=tag, **kwargs)
        _apply_dom_attrs(self, attrs)
        self.on("click", self._handle_click)

    @property
    def n_clicks(self) -> int:
        """Compat click counter (read-only observable)."""
        return self._n_clicks

    def _handle_click(self, *_args: Any, **_kwargs: Any) -> None:
        if self.disabled:
            return
        self._n_clicks += 1
        if self._on_click is not None:
            self._on_click()


class _ButtonGroupImpl(BootstrapElement):
    """Private ButtonGroup implementation."""

    component_name = "ButtonGroup"
    children_kind = "grouping"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        size: str | None = None,
        vertical: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(button_group_classes(size=size, vertical=vertical))
        super().__init__(children, **kwargs)
        _apply_dom_attrs(self, {"role": "group"})


Button, DbcButton = make_surface_classes("Button", globals())
button = Button
ButtonGroup, DbcButtonGroup = make_surface_classes("ButtonGroup", globals())
button_group = ButtonGroup
