"""Navbar family: Navbar, NavbarBrand, NavbarToggler, NavbarSimple."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui import ui

from .._base import (
    BootstrapElement,
    ChildrenError,
    PropConflictError,
    UnsupportedPropError,
    lookup_public_id,
    make_surface_classes,
)
from .._host import client_store, get_client

__all__ = [
    "Navbar",
    "DbcNavbar",
    "navbar",
    "NavbarBrand",
    "DbcNavbarBrand",
    "navbar_brand",
    "NavbarToggler",
    "DbcNavbarToggler",
    "navbar_toggler",
    "NavbarSimple",
    "DbcNavbarSimple",
    "navbar_simple",
    "navbar_structural_classes",
    "navbar_expand_class",
    "navbar_color_class",
    "navbar_position_classes",
    "navbar_theme_value",
]

_EXPAND_BREAKPOINTS: frozenset[str] = frozenset({"sm", "md", "lg", "xl", "xxl"})
_FIXED_VALUES: frozenset[str] = frozenset({"top", "bottom"})
_STICKY_VALUES: frozenset[str] = frozenset({"top"})


def _is_color_token(value: str) -> bool:
    if not value or not value[0].isalpha():
        return False
    return all(ch.isalnum() or ch in "-_" for ch in value)


def navbar_expand_class(expand: bool | str | None) -> str | None:
    """Return the ``navbar-expand-*`` class, or ``None``."""
    if expand is None or expand is False:
        return None
    if expand is True:
        return "navbar-expand"
    if isinstance(expand, str) and expand in _EXPAND_BREAKPOINTS:
        return f"navbar-expand-{expand}"
    raise ValueError(
        f"invalid expand value {expand!r}; expected True, False, None, "
        "or one of 'sm', 'md', 'lg', 'xl', 'xxl'"
    )


def navbar_color_class(color: str | None) -> str | None:
    """Return the ``bg-*`` class for a navbar color, or ``None``."""
    if color is None:
        return None
    if not _is_color_token(color):
        raise ValueError(f"invalid color value {color!r}")
    return f"bg-{color}"


def navbar_position_classes(
    *,
    fixed: str | None = None,
    sticky: str | None = None,
) -> list[str]:
    """Return ``fixed-*`` / ``sticky-*`` classes for a navbar."""
    if fixed is not None and sticky is not None:
        raise PropConflictError("fixed and sticky cannot both be set")
    classes: list[str] = []
    if fixed is not None:
        if fixed not in _FIXED_VALUES:
            raise ValueError(f"invalid fixed value {fixed!r}; expected 'top' or 'bottom'")
        classes.append(f"fixed-{fixed}")
    if sticky is not None:
        if sticky not in _STICKY_VALUES:
            raise ValueError(f"invalid sticky value {sticky!r}; expected 'top'")
        classes.append(f"sticky-{sticky}")
    return classes


def navbar_theme_value(dark: bool | None) -> str | None:
    """Return Bootstrap 5.3 ``data-bs-theme`` value for the navbar."""
    if dark is True:
        return "dark"
    return None


def navbar_structural_classes(
    *,
    color: str | None = None,
    expand: bool | str | None = None,
    fixed: str | None = None,
    sticky: str | None = None,
) -> list[str]:
    """Return Bootstrap ``navbar`` classes."""
    classes = ["navbar"]
    expand_class = navbar_expand_class(expand)
    if expand_class is not None:
        classes.append(expand_class)
    color_class = navbar_color_class(color)
    if color_class is not None:
        classes.append(color_class)
    classes.extend(navbar_position_classes(fixed=fixed, sticky=sticky))
    return classes


def _reject_removed_compat_props(surface: str, kwargs: dict[str, Any]) -> None:
    if surface == "compat" and "light" in kwargs:
        raise UnsupportedPropError("light")


def _as_children_list(children: object) -> list[Any]:
    if children is None:
        return []
    if isinstance(children, (list, tuple)):
        return list(children)
    return [children]


def _element_children(component_name: str, children: object) -> list[Any]:
    items = _as_children_list(children)
    for item in items:
        if isinstance(item, str) or not hasattr(item, "move"):
            raise ChildrenError(
                f"{component_name} does not accept text children; wrap text in a component."
            )
    return items


def _safe_get_client() -> Any:
    """Return the current NiceGUI client, or ``None`` when no UI context exists."""
    try:
        return get_client()
    except RuntimeError:
        return None


def _store_for_client(client: Any) -> Any:
    """Return the public-id store for ``client``, or ``None`` if it cannot be obtained."""
    if client is None:
        return None
    try:
        return client_store(client)
    except (RuntimeError, TypeError):
        return None


def _lookup_in_store(store: Any, public_id: str) -> Any:
    """Resolve ``public_id`` from a captured client store. Missing ids return ``None``."""
    if store is None:
        return None
    try:
        getter = store.get
    except AttributeError:
        return None
    try:
        return getter(public_id)
    except (KeyError, RuntimeError, TypeError):
        return None


class _CollapseToggleTarget:
    """Adapter exposing ``is_open`` to toggle a collapse element's ``show`` class."""

    def __init__(self, element: Any) -> None:
        self._element = element
        self._open = False

    @property
    def is_open(self) -> bool:
        return self._open

    @is_open.setter
    def is_open(self, value: bool) -> None:
        opened = bool(value)
        self._open = opened
        if opened:
            self._element.classes(add="show")
        else:
            self._element.classes(remove="show")


class _NavbarImpl(BootstrapElement):
    """Private Navbar implementation."""

    component_name = "Navbar"
    children_kind = "grouping"
    reserved_classes = ("navbar",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        color: str | None = None,
        dark: bool | None = None,
        expand: bool | str | None = None,
        fixed: str | None = None,
        sticky: str | None = None,
        tag: str = "nav",
        role: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        _reject_removed_compat_props(_surface, kwargs)
        self._structural_classes = tuple(
            navbar_structural_classes(color=color, expand=expand, fixed=fixed, sticky=sticky)
        )
        super().__init__(children, tag=tag, **kwargs)
        theme = navbar_theme_value(dark)
        if theme is not None:
            self._props["data-bs-theme"] = theme
        if role is not None:
            self._props["role"] = role


Navbar, DbcNavbar = make_surface_classes("Navbar", globals())
navbar = Navbar


class _NavbarBrandImpl(BootstrapElement):
    """Private NavbarBrand implementation."""

    component_name = "NavbarBrand"
    children_kind = "phrasing"
    reserved_classes = ("navbar-brand",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        href: str | None = None,
        external_link: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = ("navbar-brand",)
        tag = "a" if href else "span"
        super().__init__(children, tag=tag, **kwargs)
        if href:
            self._props["href"] = href
            if external_link:
                self._props["target"] = "_blank"
                self._props["rel"] = "noopener noreferrer"


NavbarBrand, DbcNavbarBrand = make_surface_classes("NavbarBrand", globals())
navbar_brand = NavbarBrand


class _NavbarTogglerImpl(BootstrapElement):
    """Private NavbarToggler implementation.

    ``target`` is a collapse component reference or a public id string.
    Clicking toggles ``target.is_open`` and does not use ``data-bs-toggle``.
    """

    component_name = "NavbarToggler"
    children_kind = "phrasing"
    reserved_classes = ("navbar-toggler",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        target: object = None,
        n_clicks: int = 0,
        on_click: Callable[..., Any] | None = None,
        type: str = "button",
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = ("navbar-toggler",)
        self._target = target
        self._n_clicks = int(n_clicks)
        self._on_click = on_click
        lookup_client = _safe_get_client()
        self._lookup_client = lookup_client
        self._id_store = _store_for_client(lookup_client)
        super().__init__(children, tag="button", **kwargs)
        self._props["type"] = type
        if children is None:
            with self:
                ui.element("span").classes("navbar-toggler-icon")
        self.on("click", self._handle_click)

    @property
    def n_clicks(self) -> int:
        return self._n_clicks

    @n_clicks.setter
    def n_clicks(self, value: int) -> None:
        self._n_clicks = int(value)

    @property
    def target(self) -> object:
        return self._target

    def _lookup_target_id(self, public_id: str) -> Any:
        client = self._lookup_client
        if client is not None:
            try:
                lookup_fn: Any = lookup_public_id
                return lookup_fn(public_id, client)
            except (RuntimeError, TypeError, KeyError, LookupError):
                pass
        return _lookup_in_store(self._id_store, public_id)

    def _resolve_target(self) -> Any:
        target = self._target
        if target is None or not isinstance(target, str):
            return target
        return self._lookup_target_id(target)

    def _toggle_target(self) -> None:
        target = self._resolve_target()
        if target is None or not hasattr(target, "is_open"):
            return
        target.is_open = not bool(target.is_open)

    def _handle_click(self, *_args: Any, **_kwargs: Any) -> None:
        self._n_clicks += 1
        self._toggle_target()
        if self._on_click is not None:
            self._on_click()


NavbarToggler, DbcNavbarToggler = make_surface_classes("NavbarToggler", globals())
navbar_toggler = NavbarToggler


class _NavbarSimpleImpl(BootstrapElement):
    """Navbar composed with brand, toggler, and collapsible content."""

    component_name = "NavbarSimple"
    children_kind = "grouping"
    reserved_classes = ("navbar",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        brand: object = None,
        brand_href: str | None = None,
        brand_external_link: bool = False,
        brand_style: Any = None,
        color: str | None = None,
        dark: bool | None = None,
        fluid: bool = False,
        links_left: bool = False,
        expand: bool | str | None = True,
        fixed: str | None = None,
        sticky: str | None = None,
        is_open: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._content: Any = None
        self._collapse_target: _CollapseToggleTarget | None = None
        _reject_removed_compat_props(_surface, kwargs)
        child_list = _element_children("NavbarSimple", children)
        self._structural_classes = tuple(
            navbar_structural_classes(color=color, expand=expand, fixed=fixed, sticky=sticky)
        )
        super().__init__(None, tag="nav", **kwargs)
        theme = navbar_theme_value(dark)
        if theme is not None:
            self._props["data-bs-theme"] = theme

        brand_type = DbcNavbarBrand if _surface == "compat" else NavbarBrand
        toggler_type = DbcNavbarToggler if _surface == "compat" else NavbarToggler
        align = "me-auto" if links_left else "ms-auto"
        container_class = "container-fluid" if fluid else "container"

        collapse_target: _CollapseToggleTarget | None = None
        content: Any = None
        with self:
            container = ui.element("div")
            container.classes(container_class)
            with container:
                if brand is not None:
                    brand_type(
                        brand,
                        href=brand_href,
                        external_link=brand_external_link,
                        style=brand_style,
                    )
                collapse = ui.element("div")
                collapse.classes("collapse navbar-collapse")
                with collapse:
                    nav_wrap = ui.element("div")
                    nav_wrap.classes(f"navbar-nav {align}")
                    for child in child_list:
                        child.move(nav_wrap)
                    content = nav_wrap
                collapse_target = _CollapseToggleTarget(collapse)
                toggler_type(target=collapse_target)
                collapse.move(container)
        self._content = content
        self._collapse_target = collapse_target
        if is_open:
            self.is_open = True

    @property
    def is_open(self) -> bool:
        if self._collapse_target is None:
            return False
        return bool(self._collapse_target.is_open)

    @is_open.setter
    def is_open(self, value: bool) -> None:
        if self._collapse_target is None:
            return
        self._collapse_target.is_open = bool(value)

    def __enter__(self) -> _NavbarSimpleImpl:
        super().__enter__()
        if self._content is not None:
            self._content.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        if self._content is not None:
            self._content.__exit__(*args)
        super().__exit__(*args)


NavbarSimple, DbcNavbarSimple = make_surface_classes("NavbarSimple", globals())
navbar_simple = NavbarSimple
