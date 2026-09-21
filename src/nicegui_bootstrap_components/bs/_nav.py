"""Navigation family: Nav, NavItem, NavLink, Breadcrumb, Pagination."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from contextlib import suppress
from typing import Any

from nicegui import ui

from .._base import (
    BootstrapElement,
    ChildrenError,
    make_surface_classes,
    normalize_style,
    style_to_css,
)
from .._host import set_element_text

__all__ = [
    "Breadcrumb",
    "DbcBreadcrumb",
    "DbcNav",
    "DbcNavItem",
    "DbcNavLink",
    "DbcPagination",
    "Nav",
    "NavItem",
    "NavLink",
    "Pagination",
    "breadcrumb",
    "breadcrumb_item_classes",
    "clamp_page",
    "nav",
    "nav_classes",
    "nav_item",
    "nav_link",
    "nav_link_classes",
    "pagination",
    "pagination_tokens",
    "validate_breadcrumb_items",
]

_VERTICAL_BPS = frozenset({"xs", "sm", "md", "lg", "xl"})
_HORIZONTAL = frozenset({"start", "center", "end", "between", "around"})
_PAGINATION_SIZES = frozenset({"sm", "lg"})
_PAGINATION_GLYPHS = {
    "first": "«",
    "prev": "‹",
    "next": "›",
    "last": "»",
}


def nav_classes(
    *,
    pills: bool = False,
    vertical: bool | str | None = False,
    horizontal: str | None = None,
    fill: bool = False,
    justified: bool = False,
    card: bool = False,
    navbar: bool = False,
    navbar_scroll: bool = False,
) -> list[str]:
    """Return Bootstrap ``nav`` classes."""
    classes = ["navbar-nav" if navbar else "nav"]
    if pills:
        classes.append("nav-pills")
    if navbar and navbar_scroll:
        classes.append("navbar-nav-scroll")
    if fill:
        classes.append("nav-fill")
    if justified:
        classes.append("nav-justified")
    if card and pills:
        classes.append("card-header-pills")
    if vertical is True:
        classes.append("flex-column")
    elif isinstance(vertical, str):
        if vertical not in _VERTICAL_BPS:
            raise ValueError(f"Invalid nav vertical breakpoint: {vertical!r}")
        classes.append(f"flex-{vertical}-column")
    elif vertical not in (False, None):
        raise ValueError(f"Invalid nav vertical: {vertical!r}")
    if horizontal is not None:
        if horizontal not in _HORIZONTAL:
            raise ValueError(f"Invalid nav horizontal: {horizontal!r}")
        classes.append(f"justify-content-{horizontal}")
    return classes


def nav_link_classes(*, active: bool | str = False, disabled: bool = False) -> list[str]:
    """Return Bootstrap ``nav-link`` classes."""
    classes = ["nav-link"]
    if active:
        classes.append("active")
    if disabled:
        classes.append("disabled")
    return classes


def breadcrumb_item_classes(active: bool = False) -> list[str]:
    """Return Bootstrap ``breadcrumb-item`` classes."""
    classes = ["breadcrumb-item"]
    if active:
        classes.append("active")
    return classes


def validate_breadcrumb_items(items: list[Any] | None) -> list[dict[str, Any]]:
    """Copy and validate breadcrumb item dicts."""
    if items is None:
        return []
    validated: list[dict[str, Any]] = []
    for entry in items:
        if not isinstance(entry, Mapping):
            raise TypeError(f"Breadcrumb items must be mappings, got {type(entry)!r}")
        if "label" not in entry:
            raise ValueError("Breadcrumb item missing label")
        label = entry["label"]
        if label is None or label == "":
            raise ValueError("Breadcrumb item missing label")
        validated.append(dict(entry))
    return validated


def _rounded_max_value(min_value: int, max_value: int, step: int) -> int:
    remainder = (max_value - min_value) % step
    if remainder != 0:
        return max_value + step - remainder
    return max_value


def pagination_tokens(
    *,
    min_value: int,
    max_value: int,
    step: int,
    active_page: int,
    fully_expanded: bool = True,
    previous_next: bool = False,
    first_last: bool = False,
) -> list[str | int]:
    """Return ordered pagination tokens (page numbers and sentinels)."""
    max_value = _rounded_max_value(min_value, max_value, step)
    tokens: list[str | int] = []
    if first_last:
        tokens.append("first")
    if previous_next:
        tokens.append("prev")
    page_count = (max_value - min_value) // step + 1
    if fully_expanded or page_count <= 7:
        page = min_value
        while page <= max_value:
            tokens.append(page)
            page += step
    else:
        tokens.append(min_value)
        if active_page <= min_value + 3 * step:
            tokens.extend(
                [
                    min_value + step,
                    min_value + 2 * step,
                    min_value + 3 * step,
                    min_value + 4 * step,
                ]
            )
            tokens.append("ellipsis")
        elif active_page >= max_value - 3 * step:
            tokens.append("ellipsis")
            tokens.extend(
                [
                    max_value - 4 * step,
                    max_value - 3 * step,
                    max_value - 2 * step,
                    max_value - step,
                ]
            )
        else:
            tokens.extend(
                [
                    "ellipsis",
                    active_page - step,
                    active_page,
                    active_page + step,
                    "ellipsis",
                ]
            )
        tokens.append(max_value)
    if previous_next:
        tokens.append("next")
    if first_last:
        tokens.append("last")
    return tokens


def clamp_page(value: int, *, min_value: int, max_value: int) -> int:
    """Clamp ``value`` into ``[min_value, max_value]``."""
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return int(value)


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


def _set_text(element: Any, text: str) -> None:
    setter = getattr(element, "set_text", None)
    if callable(setter):
        setter(text)
        return
    set_element_text(element, text)


def _flatten_children(children: object) -> list[object]:
    if children is None:
        return []
    if isinstance(children, str):
        return [children]
    if isinstance(children, (list, tuple)):
        flat: list[object] = []
        for child in children:
            flat.extend(_flatten_children(child))
        return flat
    return [children]


def _nav_link_dom_attrs(
    *,
    href: str | None,
    external_link: bool | None,
    disabled: bool,
    target: str | None,
) -> tuple[str, dict[str, Any]]:
    if href:
        attrs: dict[str, Any] = {"href": href}
        if external_link is True:
            attrs["target"] = "_blank"
            attrs["rel"] = "noopener noreferrer"
        elif target:
            attrs["target"] = target
        if disabled:
            attrs["aria-disabled"] = "true"
            attrs["tabindex"] = "-1"
        return ("a", attrs)
    button_attrs: dict[str, Any] = {"type": "button"}
    if disabled:
        button_attrs["disabled"] = True
    return ("button", button_attrs)


def _add_breadcrumb_item(
    entry: dict[str, Any],
    *,
    item_style: dict[str, Any] | None,
    item_class_name: str | None,
) -> None:
    active = bool(entry.get("active"))
    label = entry.get("label")
    href = entry.get("href")
    li = ui.element("li")
    classes = breadcrumb_item_classes(active=active)
    if item_class_name:
        classes.append(str(item_class_name))
    li.classes(" ".join(classes))
    if item_style:
        css = style_to_css(normalize_style(dict(item_style)))
        if css:
            li.style(css)
    if active:
        _apply_dom_attrs(li, {"aria-current": "page"})
        _set_text(li, str(label))
        return
    if href:
        with li:
            anchor = ui.element("a")
            attrs: dict[str, Any] = {"href": href}
            if entry.get("external_link") is True:
                attrs["target"] = "_blank"
                attrs["rel"] = "noopener noreferrer"
            elif entry.get("target"):
                attrs["target"] = entry.get("target")
            title = entry.get("title")
            if title is not None:
                attrs["title"] = title
            _apply_dom_attrs(anchor, attrs)
            _set_text(anchor, str(label))
        return
    _set_text(li, str(label))


def _adopt_breadcrumb_child(host: Any, child: object) -> None:
    if isinstance(child, (str, int, float)):
        with host:
            li = ui.element("li")
            li.classes("breadcrumb-item")
            _set_text(li, str(child))
        return
    mover = getattr(child, "move", None)
    if callable(mover):
        mover(host)
        return
    raise TypeError(f"Unsupported Breadcrumb child type: {type(child)!r}")


class _NavImpl(BootstrapElement):
    """Nav can be used to group together a collection of navigation links."""

    component_name = "Nav"
    children_kind = "auto"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        pills: bool = False,
        vertical: bool | str = False,
        horizontal: str | None = None,
        fill: bool = False,
        justified: bool = False,
        card: bool = False,
        navbar: bool = False,
        navbar_scroll: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            nav_classes(
                pills=pills,
                vertical=vertical,
                horizontal=horizontal,
                fill=fill,
                justified=justified,
                card=card,
                navbar=navbar,
                navbar_scroll=navbar_scroll,
            )
        )
        super().__init__(children, tag="ul", **kwargs)


class _NavItemImpl(BootstrapElement):
    """A list item for grouping navigation links."""

    component_name = "NavItem"
    children_kind = "auto"
    reserved_classes = ("nav-item",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = ("nav-item",)
        super().__init__(children, tag="li", **kwargs)


class _NavLinkImpl(BootstrapElement):
    """Add a link to a Nav. Can be used as a child of NavItem or of Nav directly."""

    component_name = "NavLink"
    children_kind = "phrasing"
    reserved_classes = ("nav-link",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        href: str | None = None,
        n_clicks: int = 0,
        active: bool | str = False,
        disabled: bool = False,
        external_link: bool | None = None,
        target: str | None = None,
        on_click: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        tag, attrs = _nav_link_dom_attrs(
            href=href,
            external_link=external_link,
            disabled=disabled,
            target=target,
        )
        self._structural_classes = tuple(nav_link_classes(active=active, disabled=disabled))
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


class _BreadcrumbImpl(BootstrapElement):
    """Use breadcrumbs to create a navigation breadcrumb in your app."""

    component_name = "Breadcrumb"
    children_kind = "auto"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        items: list[dict[str, Any]] | None = None,
        item_style: dict[str, Any] | None = None,
        item_class_name: str | None = None,
        tag: str = "nav",
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        alias = kwargs.pop("itemClassName", None)
        if item_class_name is None:
            item_class_name = alias
        validated = validate_breadcrumb_items(items)
        super().__init__(None, tag=tag, **kwargs)
        _apply_dom_attrs(self, {"aria-label": "breadcrumb"})
        with self:
            self._list = ui.element("ol")
            self._list.classes("breadcrumb")
            with self._list:
                for entry in validated:
                    _add_breadcrumb_item(
                        entry,
                        item_style=item_style,
                        item_class_name=item_class_name,
                    )
            for child in _flatten_children(children):
                _adopt_breadcrumb_child(self._list, child)
        self._slot_host = self._list

    def __enter__(self) -> Any:
        host = getattr(self, "_slot_host", None)
        if host is not None:
            host.__enter__()
            return self
        return super().__enter__()

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> Any:
        host = getattr(self, "_slot_host", None)
        if host is not None:
            return host.__exit__(exc_type, exc, tb)
        parent_exit = getattr(super(), "__exit__", None)
        if parent_exit is not None:
            return parent_exit(exc_type, exc, tb)
        return None


class _PaginationImpl(BootstrapElement):
    """The container for presentational components for building a pagination UI."""

    component_name = "Pagination"
    children_kind = "grouping"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        max_value: int,
        min_value: int = 1,
        step: int = 1,
        active_page: int = 1,
        size: str | None = None,
        fully_expanded: bool = True,
        previous_next: bool = False,
        first_last: bool = False,
        on_change: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        if children is not None:
            raise ChildrenError("Pagination generates its own items; do not pass children")
        if isinstance(max_value, bool) or not isinstance(max_value, int):
            raise ValueError(f"max_value must be an int, got {max_value!r}")
        if isinstance(min_value, bool) or not isinstance(min_value, int):
            raise ValueError(f"min_value must be an int, got {min_value!r}")
        if max_value < min_value:
            raise ValueError(f"max_value must be >= min_value, got {max_value} < {min_value}")
        if isinstance(step, bool) or not isinstance(step, int) or step < 1:
            raise ValueError(f"step must be an int >= 1, got {step!r}")
        if size is not None and size not in _PAGINATION_SIZES:
            raise ValueError(f"Invalid Pagination size: {size!r}")
        max_value = _rounded_max_value(min_value, max_value, step)
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        self._size = size
        self._fully_expanded = bool(fully_expanded)
        self._previous_next = bool(previous_next)
        self._first_last = bool(first_last)
        self._on_change = on_change
        self._active_page = clamp_page(int(active_page), min_value=min_value, max_value=max_value)
        super().__init__(None, tag="nav", **kwargs)
        _apply_dom_attrs(self, {"aria-label": "pagination"})
        self._render_items()

    @property
    def active_page(self) -> int:
        """Currently selected page number (clamped)."""
        return self._active_page

    @active_page.setter
    def active_page(self, value: int) -> None:
        clamped = clamp_page(int(value), min_value=self._min_value, max_value=self._max_value)
        if clamped == self._active_page:
            return
        self._active_page = clamped
        self._render_items()
        if self._on_change is not None:
            self._on_change(clamped)

    def _render_items(self) -> None:
        clearer = getattr(self, "clear", None)
        if callable(clearer):
            with suppress(Exception):
                clearer()
        classes = ["pagination"]
        if self._size == "sm":
            classes.append("pagination-sm")
        elif self._size == "lg":
            classes.append("pagination-lg")
        tokens = pagination_tokens(
            min_value=self._min_value,
            max_value=self._max_value,
            step=self._step,
            active_page=self._active_page,
            fully_expanded=self._fully_expanded,
            previous_next=self._previous_next,
            first_last=self._first_last,
        )
        with self:
            self._list = ui.element("ul")
            self._list.classes(" ".join(classes))
            with self._list:
                for token in tokens:
                    self._render_token(token)

    def _special_disabled(self, token: str) -> bool:
        if token in {"first", "prev"}:
            return self._active_page <= self._min_value
        return self._active_page >= self._max_value

    def _target_for_token(self, token: str) -> int:
        if token == "first":
            return self._min_value
        if token == "prev":
            return self._active_page - self._step
        if token == "next":
            return self._active_page + self._step
        return self._max_value

    def _bind_page_click(self, element: Any, page: int) -> None:
        def _on_click(*_args: Any, **_kwargs: Any) -> None:
            self.active_page = page

        element.on("click", _on_click)

    def _render_token(self, token: str | int) -> None:
        if token == "ellipsis":
            li = ui.element("li")
            li.classes("page-item disabled")
            with li:
                span = ui.element("span")
                span.classes("page-link")
                _set_text(span, "…")
            return
        is_active = isinstance(token, int) and token == self._active_page
        is_disabled = isinstance(token, str) and self._special_disabled(token)
        li_classes = ["page-item"]
        if is_active:
            li_classes.append("active")
        if is_disabled:
            li_classes.append("disabled")
        li = ui.element("li")
        li.classes(" ".join(li_classes))
        if is_active:
            _apply_dom_attrs(li, {"aria-current": "page"})
        with li:
            anchor = ui.element("a")
            anchor.classes("page-link")
            if isinstance(token, int):
                if is_active:
                    with anchor:
                        _set_text(ui.element("span"), str(token))
                        hidden = ui.element("span")
                        hidden.classes("visually-hidden")
                        _set_text(hidden, "(current)")
                else:
                    _set_text(anchor, str(token))
                self._bind_page_click(anchor, token)
                return
            glyph = _PAGINATION_GLYPHS[token]
            hidden_label: str | None = None
            if not is_disabled and token == "prev":
                hidden_label = "Previous"
            elif not is_disabled and token == "next":
                hidden_label = "Next"
            if hidden_label is None:
                _set_text(anchor, glyph)
            else:
                with anchor:
                    _set_text(ui.element("span"), glyph)
                    hidden = ui.element("span")
                    hidden.classes("visually-hidden")
                    _set_text(hidden, hidden_label)
            if not is_disabled:
                self._bind_page_click(anchor, self._target_for_token(token))


Nav, DbcNav = make_surface_classes("Nav", globals())
nav = Nav
NavItem, DbcNavItem = make_surface_classes("NavItem", globals())
nav_item = NavItem
NavLink, DbcNavLink = make_surface_classes("NavLink", globals())
nav_link = NavLink
Breadcrumb, DbcBreadcrumb = make_surface_classes("Breadcrumb", globals())
breadcrumb = Breadcrumb
Pagination, DbcPagination = make_surface_classes("Pagination", globals())
pagination = Pagination
