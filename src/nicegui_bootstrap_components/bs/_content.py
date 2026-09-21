"""Content family: Card, ListGroup, Table, Badge, Progress, Placeholder."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from contextvars import ContextVar, Token
from typing import Any, cast

from nicegui import ui

from .._base import (
    BootstrapElement,
    ChildrenError,
    PropConflictError,
    UnsupportedPropError,
    make_surface_classes,
    normalize_style,
    resolve_class_name,
    style_to_css,
)
from .._host import set_element_text

__all__ = [
    "Badge",
    "Card",
    "CardBody",
    "CardFooter",
    "CardGroup",
    "CardHeader",
    "CardImg",
    "CardImgOverlay",
    "CardLink",
    "DbcBadge",
    "DbcCard",
    "DbcCardBody",
    "DbcCardFooter",
    "DbcCardGroup",
    "DbcCardHeader",
    "DbcCardImg",
    "DbcCardImgOverlay",
    "DbcCardLink",
    "DbcListGroup",
    "DbcListGroupItem",
    "DbcPlaceholder",
    "DbcProgress",
    "DbcTable",
    "ListGroup",
    "ListGroupItem",
    "Placeholder",
    "Progress",
    "Table",
    "badge",
    "badge_structural_classes",
    "card",
    "card_body",
    "card_footer",
    "card_group",
    "card_header",
    "card_img",
    "card_img_overlay",
    "card_img_structural_classes",
    "card_link",
    "card_structural_classes",
    "format_table_cell",
    "grouped_spans",
    "list_group",
    "list_group_item",
    "list_group_item_structural_classes",
    "list_group_structural_classes",
    "placeholder",
    "placeholder_structural_classes",
    "progress",
    "progress_bar_structural_classes",
    "progress_percent",
    "progress_structural_classes",
    "resolve_list_group_item_tag",
    "resolve_list_group_tag",
    "table",
    "table_responsive_class",
    "table_structural_classes",
]

_BOOTSTRAP_CONTEXT_COLORS = frozenset(
    {
        "primary",
        "secondary",
        "success",
        "danger",
        "warning",
        "info",
        "light",
        "dark",
    }
)
_TEXT_COLORS = _BOOTSTRAP_CONTEXT_COLORS | frozenset(
    {
        "white",
        "black",
        "muted",
        "body",
        "body-secondary",
        "body-tertiary",
    }
)
_BREAKPOINTS = frozenset({"sm", "md", "lg", "xl", "xxl"})
_PLACEHOLDER_SIZES = frozenset({"xs", "sm", "lg"})
_PLACEHOLDER_ANIMATIONS = frozenset({"glow", "wave"})
_WIDTH_UTILITIES = frozenset({25, 50, 75, 100})
_DISPLAY_UTILITIES = frozenset(
    {"inline", "inline-block", "block", "flex", "grid", "table", "inline-flex"}
)
_UNITLESS_STYLE = frozenset(
    {
        "opacity",
        "flex",
        "grow",
        "shrink",
        "order",
        "z-index",
        "font-weight",
        "line-height",
    }
)

_LIST_GROUP_ITEM_DEFAULT_TAG: ContextVar[str | None] = ContextVar(
    "_list_group_item_default_tag",
    default=None,
)
_PROGRESS_NESTED: ContextVar[bool] = ContextVar("_progress_nested", default=False)


def _validate_color(color: str, *, allowed: frozenset[str] | None = None) -> str:
    palette = _BOOTSTRAP_CONTEXT_COLORS if allowed is None else allowed
    if color not in palette:
        raise ValueError(f"Unknown color {color!r}")
    return color


def _col_width_classes(breakpoint: str, value: int | bool | None) -> list[str]:
    if value is None or value is False:
        return []
    if value is True:
        return ["col"] if breakpoint == "xs" else [f"col-{breakpoint}"]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Unknown column width {value!r}")
    if value < 1 or value > 12:
        raise ValueError(f"Unknown column width {value!r}")
    if breakpoint == "xs":
        return [f"col-{value}"]
    return [f"col-{breakpoint}-{value}"]


def _children_present(children: object) -> bool:
    if children is None:
        return False
    return not (children == "" or children == [] or children == ())


def _declared_children(children: object) -> list[object]:
    if children is None:
        return []
    if isinstance(children, (list, tuple)):
        return list(children)
    return [children]


def _is_float_like(value: object) -> bool:
    if isinstance(value, (bool, int)):
        return False
    if isinstance(value, float):
        return True
    return "float" in type(value).__name__.lower()


def _format_number(value: float) -> str:
    if value == int(value):
        return str(int(value))
    return str(value)


def _merge_width_style(width_pct: float, bar_style: dict[str, Any] | str | None) -> str:
    if isinstance(bar_style, str) and bar_style:
        return f"width: {width_pct}%; {bar_style}"
    style_dict: dict[str, Any] = {"width": f"{width_pct}%"}
    if isinstance(bar_style, dict):
        style_dict.update(bar_style)
    normalized: dict[str, str] | str = normalize_style(style_dict)
    if isinstance(normalized, str):
        return normalized
    converted = style_to_css(normalized)
    return converted if isinstance(converted, str) else str(converted)


def _merge_style_kwarg(kwargs: dict[str, Any], extra: dict[str, Any]) -> None:
    style = kwargs.get("style")
    if style is None:
        kwargs["style"] = dict(extra)
        return
    if isinstance(style, dict):
        merged = dict(extra)
        merged.update(style)
        kwargs["style"] = merged
        return
    suffix = "; ".join(f"{key}: {value}" for key, value in extra.items())
    kwargs["style"] = f"{style}; {suffix}"


def _require_pandas() -> Any:
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "pandas is required for Table.from_dataframe. "
            "Install the pandas extra to use this helper."
        ) from exc
    return pd


def _apply_interactive_props(
    element: Any,
    *,
    tag: str,
    href: str | None = None,
    disabled: bool = False,
    external_link: bool = False,
) -> None:
    if tag == "a":
        if href is not None:
            element._props["href"] = href
        if external_link:
            element._props["target"] = "_blank"
            element._props["rel"] = "noopener noreferrer"
        if disabled:
            element._props["aria-disabled"] = "true"
            element._props["tabindex"] = "-1"
        return
    if tag == "button":
        element._props.setdefault("type", "button")
        if disabled:
            element._props["disabled"] = True
        return
    if disabled:
        element._props["aria-disabled"] = "true"


def _place_children(host: Any, children: object) -> None:
    if children is None:
        return
    if isinstance(children, str):
        raise ChildrenError("Table does not accept text children; wrap text in a component")
    for child in _declared_children(children):
        if isinstance(child, str):
            raise ChildrenError("Table does not accept text children; wrap text in a component")
        move = getattr(child, "move", None)
        if callable(move):
            move(host)


def _configure_progress_bar(
    target: Any,
    *,
    classes: list[str],
    value: float,
    min_value: float,
    max_value: float,
    label: str | None,
    bar_style: dict[str, Any] | str | None,
) -> None:
    if classes and hasattr(target, "classes"):
        target.classes(" ".join(classes))
    target._props["role"] = "progressbar"
    target._props["aria-valuenow"] = _format_number(value)
    target._props["aria-valuemin"] = _format_number(min_value)
    target._props["aria-valuemax"] = _format_number(max_value)
    target._props["style"] = _merge_width_style(
        progress_percent(value, min_value, max_value),
        bar_style,
    )
    if label is not None:
        set_element_text(target, str(label))


def card_structural_classes(
    *,
    color: str | None = None,
    outline: bool = False,
    inverse: bool = False,
    body: bool = False,
) -> list[str]:
    """Return Bootstrap ``card`` classes."""
    classes = ["card"]
    if body:
        classes.append("card-body")
    if color is not None:
        _validate_color(color)
        if outline:
            classes.append(f"border-{color}")
        else:
            classes.append(f"text-bg-{color}")
    if inverse:
        classes.append("text-white")
    return classes


def card_img_structural_classes(
    *,
    top: bool = False,
    bottom: bool = False,
    overlay: bool = False,
) -> list[str]:
    """Return Bootstrap ``card-img`` position classes."""
    selected = [
        name for name, flag in (("top", top), ("bottom", bottom), ("overlay", overlay)) if flag
    ]
    if len(selected) > 1:
        raise PropConflictError("top")
    if top:
        return ["card-img-top"]
    if bottom:
        return ["card-img-bottom"]
    return ["card-img"]


def list_group_structural_classes(
    *,
    flush: bool = False,
    numbered: bool = False,
    horizontal: bool | str = False,
) -> list[str]:
    """Return Bootstrap ``list-group`` classes."""
    classes = ["list-group"]
    if flush:
        classes.append("list-group-flush")
    if numbered:
        classes.append("list-group-numbered")
    if horizontal is True:
        classes.append("list-group-horizontal")
    elif horizontal is False:
        pass
    elif isinstance(horizontal, str) and horizontal in _BREAKPOINTS:
        classes.append(f"list-group-horizontal-{horizontal}")
    else:
        raise ValueError(f"Unknown horizontal breakpoint {horizontal!r}")
    return classes


def list_group_item_structural_classes(
    *,
    active: bool = False,
    disabled: bool = False,
    color: str | None = None,
    action: bool = False,
    href: str | None = None,
) -> list[str]:
    """Return Bootstrap ``list-group-item`` classes."""
    classes = ["list-group-item"]
    if color is not None:
        _validate_color(color)
        classes.append(f"list-group-item-{color}")
    if action or href is not None:
        classes.append("list-group-item-action")
    if active:
        classes.append("active")
    if disabled:
        classes.append("disabled")
    return classes


def resolve_list_group_tag(*, tag: str | None = None, numbered: bool = False) -> str:
    """Return the ListGroup tag fixed at construction time."""
    if tag is not None:
        return tag
    if numbered:
        return "ol"
    return "div"


def resolve_list_group_item_tag(
    *,
    tag: str | None = None,
    href: str | None = None,
    action: bool = False,
    context_default: str | None = None,
) -> str:
    """Return the ListGroupItem tag from explicit tag, href, action, then context."""
    if tag is not None:
        return tag
    if href is not None:
        return "a"
    if action:
        return "button"
    if context_default is not None:
        return context_default
    return "div"


def table_structural_classes(
    *,
    bordered: bool = False,
    borderless: bool = False,
    striped: bool = False,
    hover: bool = False,
    small: bool = False,
    size: str | None = None,
    color: str | None = None,
    striped_columns: bool = False,
) -> list[str]:
    """Return Bootstrap ``table`` classes."""
    if bordered and borderless:
        raise PropConflictError("bordered")
    if small and size is not None and size != "sm":
        raise PropConflictError("small")
    classes = ["table"]
    if bordered:
        classes.append("table-bordered")
    if borderless:
        classes.append("table-borderless")
    if striped:
        classes.append("table-striped")
    if striped_columns:
        classes.append("table-striped-columns")
    if hover:
        classes.append("table-hover")
    if small or size == "sm":
        classes.append("table-sm")
    elif size is not None:
        raise ValueError(f"Unknown table size {size!r}")
    if color is not None:
        _validate_color(color)
        classes.append(f"table-{color}")
    return classes


def table_responsive_class(responsive: bool | str) -> str | None:
    """Return the wrapper class for a responsive table, or ``None``."""
    if responsive is False:
        return None
    if responsive is True:
        return "table-responsive"
    if isinstance(responsive, str) and responsive in _BREAKPOINTS:
        return f"table-responsive-{responsive}"
    raise ValueError(f"Unknown responsive breakpoint {responsive!r}")


def grouped_spans(values: list[object] | tuple[object, ...]) -> list[tuple[object, int]]:
    """Group consecutive equal values into ``(value, colspan)`` pairs."""
    if not values:
        return []
    grouped: list[tuple[object, int]] = []
    current = values[0]
    count = 1
    for item in values[1:]:
        if item == current:
            count += 1
        else:
            grouped.append((current, count))
            current = item
            count = 1
    grouped.append((current, count))
    return grouped


def format_table_cell(
    value: object,
    *,
    date_format: str | None = None,
    float_format: str | Callable[..., Any] | None = None,
) -> str:
    """Format a table cell the way DBC ``from_dataframe`` does."""
    if value is None:
        return ""
    if isinstance(value, tuple):
        return " ".join(
            format_table_cell(part, date_format=date_format, float_format=float_format)
            for part in value
        )
    if date_format is not None:
        strftime = getattr(value, "strftime", None)
        if callable(strftime):
            try:
                return str(strftime(date_format))
            except (TypeError, ValueError):
                pass
    if float_format is not None and _is_float_like(value):
        number = float(cast(float, value))
        if callable(float_format):
            return str(float_format(number))
        if "%" in float_format:
            return float_format % number
        try:
            return format(number, float_format)
        except ValueError:
            return str(value)
    return str(value)


def badge_structural_classes(
    *,
    color: str = "secondary",
    pill: bool = False,
    text_color: str | None = None,
) -> list[str]:
    """Return Bootstrap ``badge`` classes."""
    _validate_color(color)
    classes = ["badge", f"text-bg-{color}"]
    if text_color is not None:
        _validate_color(text_color, allowed=_TEXT_COLORS)
        classes.append(f"text-{text_color}")
    if pill:
        classes.append("rounded-pill")
    return classes


def progress_structural_classes() -> list[str]:
    """Return Bootstrap ``progress`` wrapper classes."""
    return ["progress"]


def progress_bar_structural_classes(
    *,
    color: str | None = None,
    striped: bool = False,
    animated: bool = False,
) -> list[str]:
    """Return Bootstrap ``progress-bar`` classes."""
    classes = ["progress-bar"]
    if color is not None:
        _validate_color(color)
        classes.append(f"bg-{color}")
    if striped or animated:
        classes.append("progress-bar-striped")
    if animated:
        classes.append("progress-bar-animated")
    return classes


def progress_percent(value: float, min_value: float, max_value: float) -> float:
    """Return a clamped 0-100 width percentage for a determinate bar."""
    if max_value == min_value:
        return 0.0
    percent = (value - min_value) / (max_value - min_value) * 100.0
    if percent < 0.0:
        return 0.0
    if percent > 100.0:
        return 100.0
    return round(percent, 4)


def placeholder_structural_classes(
    *,
    animation: str | None = None,
    size: str | None = None,
    color: str | None = None,
    button: bool = False,
    display: bool | str | None = None,
    width: int | str | None = None,
    xs: int | bool | None = None,
    sm: int | bool | None = None,
    md: int | bool | None = None,
    lg: int | bool | None = None,
    xl: int | bool | None = None,
    xxl: int | bool | None = None,
) -> list[str]:
    """Return Bootstrap ``placeholder`` classes."""
    classes = ["placeholder"]
    if button:
        classes.append("btn")
        classes.append("disabled")
        if color is not None:
            _validate_color(color)
            classes.append(f"btn-{color}")
    elif color is not None:
        _validate_color(color)
        classes.append(f"bg-{color}")
    if animation is not None:
        if animation not in _PLACEHOLDER_ANIMATIONS:
            raise ValueError(f"Unknown placeholder animation {animation!r}")
        classes.append(f"placeholder-{animation}")
    if size is not None:
        if size not in _PLACEHOLDER_SIZES:
            raise ValueError(f"Unknown placeholder size {size!r}")
        classes.append(f"placeholder-{size}")
    for breakpoint, value in (
        ("xs", xs),
        ("sm", sm),
        ("md", md),
        ("lg", lg),
        ("xl", xl),
        ("xxl", xxl),
    ):
        classes.extend(_col_width_classes(breakpoint, value))
    if isinstance(width, bool) or (width is not None and not isinstance(width, (int, str))):
        raise ValueError(f"Unknown placeholder width {width!r}")
    if isinstance(width, int):
        if width in _WIDTH_UTILITIES:
            classes.append(f"w-{width}")
        elif 1 <= width <= 12:
            classes.append(f"col-{width}")
        else:
            raise ValueError(f"Unknown placeholder width {width!r}")
    if display is False or display == "none":
        classes.append("d-none")
    elif display is True or display in {None, "show", "auto"}:
        pass
    elif isinstance(display, str) and display in _DISPLAY_UTILITIES:
        classes.append(f"d-{display}")
    elif display is not None:
        raise ValueError(f"Unknown display {display!r}")
    return classes


def _index_header_label(df: Any, index_label: str | None) -> str:
    if index_label is not None:
        return index_label
    name = getattr(df.index, "name", None)
    if name is not None:
        return str(name)
    names = getattr(df.index, "names", None)
    if names:
        parts = [str(part) for part in names if part is not None]
        return " ".join(parts)
    return ""


def _write_dataframe_header(df: Any, *, index: bool, index_label: str | None) -> None:
    index_label_text = _index_header_label(df, index_label) if index else ""
    columns = df.columns
    nlevels = int(getattr(columns, "nlevels", 1))
    if nlevels > 1 and hasattr(columns, "get_level_values"):
        for level in range(nlevels):
            with ui.element("tr"):
                if index:
                    th = ui.element("th")
                    set_element_text(th, index_label_text if level == nlevels - 1 else "")
                values = list(columns.get_level_values(level))
                for value, span in grouped_spans(values):
                    th = ui.element("th")
                    set_element_text(th, "" if value is None else str(value))
                    if span > 1:
                        th._props["colspan"] = span
        return
    with ui.element("tr"):
        if index:
            th = ui.element("th")
            set_element_text(th, index_label_text)
        for col in columns:
            th = ui.element("th")
            set_element_text(th, "" if col is None else str(col))


def _write_dataframe_body(
    df: Any,
    *,
    index: bool,
    date_format: str | None,
    float_format: str | Callable[..., Any] | None,
) -> None:
    for idx, row in df.iterrows():
        with ui.element("tr"):
            if index:
                th = ui.element("th")
                set_element_text(
                    th, format_table_cell(idx, date_format=date_format, float_format=float_format)
                )
                th._props["scope"] = "row"
            for col in df.columns:
                td = ui.element("td")
                set_element_text(
                    td,
                    format_table_cell(row[col], date_format=date_format, float_format=float_format),
                )


class _CardImpl(BootstrapElement):
    """Private Card implementation."""

    component_name = "Card"
    children_kind = "auto"
    reserved_classes = ("card",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        color: str | None = None,
        outline: bool = False,
        inverse: bool = False,
        body: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            card_structural_classes(color=color, outline=outline, inverse=inverse, body=body)
        )
        tag = kwargs.pop("tag", "div")
        super().__init__(children, tag=tag, **kwargs)


Card, DbcCard = make_surface_classes("Card", globals())
card = Card


class _CardBodyImpl(BootstrapElement):
    """Private CardBody implementation."""

    component_name = "CardBody"
    children_kind = "auto"
    reserved_classes = ("card-body",)

    def __init__(self, children: object = None, *, _surface: str, **kwargs: Any) -> None:
        self._surface = _surface
        self._structural_classes = ("card-body",)
        tag = kwargs.pop("tag", "div")
        super().__init__(children, tag=tag, **kwargs)


CardBody, DbcCardBody = make_surface_classes("CardBody", globals())
card_body = CardBody


class _CardHeaderImpl(BootstrapElement):
    """Private CardHeader implementation."""

    component_name = "CardHeader"
    children_kind = "auto"
    reserved_classes = ("card-header",)

    def __init__(self, children: object = None, *, _surface: str, **kwargs: Any) -> None:
        self._surface = _surface
        self._structural_classes = ("card-header",)
        tag = kwargs.pop("tag", "div")
        super().__init__(children, tag=tag, **kwargs)


CardHeader, DbcCardHeader = make_surface_classes("CardHeader", globals())
card_header = CardHeader


class _CardFooterImpl(BootstrapElement):
    """Private CardFooter implementation."""

    component_name = "CardFooter"
    children_kind = "auto"
    reserved_classes = ("card-footer",)

    def __init__(self, children: object = None, *, _surface: str, **kwargs: Any) -> None:
        self._surface = _surface
        self._structural_classes = ("card-footer",)
        tag = kwargs.pop("tag", "div")
        super().__init__(children, tag=tag, **kwargs)


CardFooter, DbcCardFooter = make_surface_classes("CardFooter", globals())
card_footer = CardFooter


class _CardGroupImpl(BootstrapElement):
    """Private CardGroup implementation."""

    component_name = "CardGroup"
    children_kind = "grouping"
    reserved_classes = ("card-group",)

    def __init__(self, children: object = None, *, _surface: str, **kwargs: Any) -> None:
        self._surface = _surface
        self._structural_classes = ("card-group",)
        tag = kwargs.pop("tag", "div")
        super().__init__(children, tag=tag, **kwargs)


CardGroup, DbcCardGroup = make_surface_classes("CardGroup", globals())
card_group = CardGroup


class _CardImgImpl(BootstrapElement):
    """Private CardImg implementation."""

    component_name = "CardImg"
    children_kind = "auto"
    reserved_classes = ()

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        src: str | None = None,
        alt: str = "",
        top: bool = False,
        bottom: bool = False,
        overlay: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            card_img_structural_classes(top=top, bottom=bottom, overlay=overlay)
        )
        tag = kwargs.pop("tag", "img")
        super().__init__(children, tag=tag, **kwargs)
        if src is not None:
            self._props["src"] = src
        self._props["alt"] = alt


CardImg, DbcCardImg = make_surface_classes("CardImg", globals())
card_img = CardImg


class _CardImgOverlayImpl(BootstrapElement):
    """Private CardImgOverlay implementation."""

    component_name = "CardImgOverlay"
    children_kind = "auto"
    reserved_classes = ("card-img-overlay",)

    def __init__(self, children: object = None, *, _surface: str, **kwargs: Any) -> None:
        self._surface = _surface
        self._structural_classes = ("card-img-overlay",)
        tag = kwargs.pop("tag", "div")
        super().__init__(children, tag=tag, **kwargs)


CardImgOverlay, DbcCardImgOverlay = make_surface_classes("CardImgOverlay", globals())
card_img_overlay = CardImgOverlay


class _CardLinkImpl(BootstrapElement):
    """Private CardLink implementation. Click listener is registered in ``__init__`` only."""

    component_name = "CardLink"
    children_kind = "phrasing"
    reserved_classes = ("card-link",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        href: str | None = None,
        external_link: bool = False,
        n_clicks: int = 0,
        on_click: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = ("card-link",)
        self._n_clicks = int(n_clicks)
        self._on_click = on_click
        kwargs.pop("tag", None)
        super().__init__(children, tag="a", **kwargs)
        _apply_interactive_props(self, tag="a", href=href, external_link=external_link)
        self.on("click", self._handle_click)

    def _handle_click(self, *_args: Any, **_kwargs: Any) -> None:
        self._n_clicks += 1
        if self._on_click is not None:
            self._on_click()


CardLink, DbcCardLink = make_surface_classes("CardLink", globals())
card_link = CardLink


class _ListGroupImpl(BootstrapElement):
    """Private ListGroup implementation. Tag is fixed in ``__init__``."""

    component_name = "ListGroup"
    children_kind = "grouping"
    reserved_classes = ("list-group",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        flush: bool = False,
        numbered: bool = False,
        horizontal: bool | str = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            list_group_structural_classes(flush=flush, numbered=numbered, horizontal=horizontal)
        )
        explicit_tag = kwargs.pop("tag", None)
        self._resolved_tag = resolve_list_group_tag(tag=explicit_tag, numbered=numbered)
        super().__init__(children, tag=self._resolved_tag, **kwargs)

    def __enter__(self) -> Any:
        if self._surface == "native":
            default = "li" if self._resolved_tag in {"ul", "ol"} else "div"
            self._item_tag_token: Token[str | None] | None = _LIST_GROUP_ITEM_DEFAULT_TAG.set(
                default
            )
        return super().__enter__()

    def __exit__(self, *args: Any) -> Any:
        try:
            return super().__exit__(*args)
        finally:
            token = getattr(self, "_item_tag_token", None)
            if token is not None:
                _LIST_GROUP_ITEM_DEFAULT_TAG.reset(token)
                self._item_tag_token = None


ListGroup, DbcListGroup = make_surface_classes("ListGroup", globals())
list_group = ListGroup


class _ListGroupItemImpl(BootstrapElement):
    """Private ListGroupItem implementation. Click listener is registered in ``__init__`` only."""

    component_name = "ListGroupItem"
    children_kind = "auto"
    reserved_classes = ("list-group-item",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        active: bool = False,
        disabled: bool = False,
        color: str | None = None,
        action: bool = False,
        href: str | None = None,
        external_link: bool = False,
        n_clicks: int = 0,
        on_click: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            list_group_item_structural_classes(
                active=active,
                disabled=disabled,
                color=color,
                action=action,
                href=href,
            )
        )
        explicit_tag = kwargs.pop("tag", None)
        self._resolved_tag = resolve_list_group_item_tag(
            tag=explicit_tag,
            href=href,
            action=action,
            context_default=_LIST_GROUP_ITEM_DEFAULT_TAG.get(),
        )
        self._n_clicks = int(n_clicks)
        self._on_click = on_click
        super().__init__(children, tag=self._resolved_tag, **kwargs)
        _apply_interactive_props(
            self,
            tag=self._resolved_tag,
            href=href,
            disabled=disabled,
            external_link=external_link,
        )
        self.on("click", self._handle_click)

    def _handle_click(self, *_args: Any, **_kwargs: Any) -> None:
        self._n_clicks += 1
        if self._on_click is not None:
            self._on_click()


ListGroupItem, DbcListGroupItem = make_surface_classes("ListGroupItem", globals())
list_group_item = ListGroupItem


class _TableImpl(BootstrapElement):
    """Private Table implementation."""

    component_name = "Table"
    children_kind = "grouping"
    reserved_classes = ()

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        bordered: bool = False,
        borderless: bool = False,
        striped: bool = False,
        hover: bool = False,
        size: str | None = None,
        responsive: bool | str = False,
        color: str | None = None,
        striped_columns: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._inner: ui.element | None = None
        if "dark" in kwargs:
            kwargs.pop("dark")
            if _surface == "compat":
                raise UnsupportedPropError("dark")
            raise ValueError("Table dark was removed; color mode comes from theme")
        small = False
        if "small" in kwargs:
            if _surface == "compat":
                raise UnsupportedPropError("small")
            small = bool(kwargs.pop("small"))
        tbl_classes = table_structural_classes(
            bordered=bordered,
            borderless=borderless,
            striped=striped,
            hover=hover,
            small=small,
            size=size,
            color=color,
            striped_columns=striped_columns,
        )
        resp_class = table_responsive_class(responsive)
        if resp_class is not None:
            user_class: str | None = None
            class_name = kwargs.pop("class_name", None)
            class_name_camel = kwargs.pop("className", None)
            if class_name is not None or class_name_camel is not None:
                user_class = resolve_class_name(class_name, class_name_camel, self._surface)
            self._structural_classes: tuple[str, ...] = (resp_class,)
            super().__init__(None, tag="div", **kwargs)
            inner = ui.element("table")
            inner.classes(" ".join(tbl_classes))
            if user_class:
                inner.classes(user_class)
            inner.move(self)
            self._inner = inner
            _place_children(inner, children)
            return
        self._structural_classes = tuple(tbl_classes)
        super().__init__(children, tag="table", **kwargs)

    def __enter__(self) -> Any:
        if self._inner is not None:
            return self._inner.__enter__()
        return super().__enter__()

    def __exit__(self, *args: Any) -> Any:
        if self._inner is not None:
            return self._inner.__exit__(*args)
        return super().__exit__(*args)

    @classmethod
    def from_dataframe(
        cls,
        df: object,
        *,
        columns: str | Sequence[str] | None = None,
        header: bool = True,
        index: bool = True,
        index_label: str | None = None,
        date_format: str | None = None,
        float_format: str | Callable[..., Any] | None = None,
        caption: str | None = None,
        **table_props: Any,
    ) -> _TableImpl:
        """Build a Table from a pandas DataFrame.

        pandas is an optional extra. Missing pandas raises ImportError.
        """
        pd_mod = _require_pandas()
        frame = df if isinstance(df, pd_mod.DataFrame) else pd_mod.DataFrame(df)
        if columns is not None:
            col_list = [columns] if isinstance(columns, str) else list(columns)
            frame = frame.loc[:, col_list]
        table = cls(**table_props)
        with table:
            if caption is not None:
                cap_el = ui.element("caption")
                set_element_text(cap_el, str(caption))
            if header:
                with ui.element("thead"):
                    _write_dataframe_header(frame, index=index, index_label=index_label)
            with ui.element("tbody"):
                _write_dataframe_body(
                    frame,
                    index=index,
                    date_format=date_format,
                    float_format=float_format,
                )
        return table


Table, DbcTable = make_surface_classes("Table", globals())
table = Table


class _BadgeImpl(BootstrapElement):
    """Private Badge implementation. Click listener is registered in ``__init__`` only."""

    component_name = "Badge"
    children_kind = "phrasing"
    reserved_classes = ("badge",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        color: str = "secondary",
        pill: bool = False,
        text_color: str | None = None,
        href: str | None = None,
        external_link: bool = False,
        n_clicks: int = 0,
        on_click: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            badge_structural_classes(color=color, pill=pill, text_color=text_color)
        )
        explicit_tag = kwargs.pop("tag", None)
        resolved_tag = "a" if href is not None else (explicit_tag or "span")
        self._n_clicks = int(n_clicks)
        self._on_click = on_click
        super().__init__(children, tag=resolved_tag, **kwargs)
        _apply_interactive_props(self, tag=resolved_tag, href=href, external_link=external_link)
        self.on("click", self._handle_click)

    def _handle_click(self, *_args: Any, **_kwargs: Any) -> None:
        self._n_clicks += 1
        if self._on_click is not None:
            self._on_click()


Badge, DbcBadge = make_surface_classes("Badge", globals())
badge = Badge


class _ProgressImpl(BootstrapElement):
    """Private Progress implementation."""

    component_name = "Progress"
    children_kind = "auto"
    reserved_classes = ()

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        value: float = 0,
        min: float = 0,
        max: float = 100,
        label: str | None = None,
        animated: bool = False,
        striped: bool = False,
        color: str | None = None,
        height: int | float | str | None = None,
        bar: bool = False,
        bar_class_name: str | None = None,
        barClassName: str | None = None,
        bar_style: dict[str, Any] | str | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        min_value = float(min)
        max_value = float(max)
        value_n = float(value)
        self._value = value_n
        self._min = min_value
        self._max = max_value
        self._label = label
        self._bar_style = bar_style
        extra_bar = None
        if bar_class_name is not None or barClassName is not None:
            extra_bar = resolve_class_name(bar_class_name, barClassName, self._surface)
        self._bar_classes = progress_bar_structural_classes(
            color=color, striped=striped, animated=animated
        )
        if extra_bar:
            self._bar_classes = [*self._bar_classes, extra_bar]
        self._nested = bool(bar) or _PROGRESS_NESTED.get()
        kwargs.pop("tag", None)
        if height is not None and not self._nested:
            if isinstance(height, bool):
                raise ValueError("height must be a CSS length or number of pixels")
            height_css = f"{height}px" if isinstance(height, (int, float)) else str(height)
            _merge_style_kwarg(kwargs, {"height": height_css})
        if self._nested:
            self._structural_classes = tuple(self._bar_classes)
            super().__init__(children, tag="div", **kwargs)
            _configure_progress_bar(
                self,
                classes=[],
                value=value_n,
                min_value=min_value,
                max_value=max_value,
                label=label,
                bar_style=bar_style,
            )
            self._bar = None
            return
        self._structural_classes = tuple(progress_structural_classes())
        super().__init__(children, tag="div", **kwargs)
        bar_el = ui.element("div")
        _configure_progress_bar(
            bar_el,
            classes=self._bar_classes,
            value=value_n,
            min_value=min_value,
            max_value=max_value,
            label=label,
            bar_style=bar_style,
        )
        bar_el.move(self, target_index=0)
        self._bar = bar_el
        self._convert_nested_progress_children(children)

    def _convert_nested_progress_children(self, children: object) -> None:
        if children is None or isinstance(children, str):
            return
        for child in _declared_children(children):
            convert = getattr(child, "_become_nested_bar", None)
            if callable(convert):
                convert()

    def _become_nested_bar(self) -> None:
        if self._nested:
            return
        self._nested = True
        self.classes(remove="progress")
        extra = " ".join(self._bar_classes)
        if extra:
            self.classes(add=extra)
        label = self._label
        bar = getattr(self, "_bar", None)
        if bar is not None:
            bar_text = getattr(bar, "text", None)
            if bar_text:
                label = str(bar_text)
            delete = getattr(bar, "delete", None)
            if callable(delete):
                delete()
            self._bar = None
        _configure_progress_bar(
            self,
            classes=[],
            value=self._value,
            min_value=self._min,
            max_value=self._max,
            label=label,
            bar_style=self._bar_style,
        )

    def __enter__(self) -> Any:
        self._nested_token: Token[bool] | None = _PROGRESS_NESTED.set(True)
        try:
            return super().__enter__()
        except BaseException:
            _PROGRESS_NESTED.reset(self._nested_token)
            raise

    def __exit__(self, *args: Any) -> Any:
        try:
            return super().__exit__(*args)
        finally:
            token = getattr(self, "_nested_token", None)
            if token is not None:
                _PROGRESS_NESTED.reset(token)
                self._nested_token = None


Progress, DbcProgress = make_surface_classes("Progress", globals())
progress = Progress


class _PlaceholderImpl(BootstrapElement):
    """Private Placeholder implementation."""

    component_name = "Placeholder"
    children_kind = "auto"
    reserved_classes = ("placeholder",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        animation: str | None = None,
        size: str | None = None,
        color: str | None = None,
        button: bool = False,
        loading: bool = False,
        display: bool | str | None = None,
        width: int | str | None = None,
        xs: int | bool | None = None,
        sm: int | bool | None = None,
        md: int | bool | None = None,
        lg: int | bool | None = None,
        xl: int | bool | None = None,
        xxl: int | bool | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        width_for_classes: int | None
        if isinstance(width, bool):
            raise ValueError(f"Unknown placeholder width {width!r}")
        width_for_classes = width if isinstance(width, int) else None
        self._structural_classes = tuple(
            placeholder_structural_classes(
                animation=animation,
                size=size,
                color=color,
                button=button,
                display=display,
                width=width_for_classes,
                xs=xs,
                sm=sm,
                md=md,
                lg=lg,
                xl=xl,
                xxl=xxl,
            )
        )
        explicit_tag = kwargs.pop("tag", None)
        if explicit_tag:
            resolved_tag = explicit_tag
        elif button:
            resolved_tag = "button"
        else:
            resolved_tag = "span"
        if isinstance(width, str):
            _merge_style_kwarg(kwargs, {"width": width})
        super().__init__(children, tag=resolved_tag, **kwargs)
        if resolved_tag == "button":
            self._props.setdefault("type", "button")
            self._props["disabled"] = True
        elif button:
            self._props["disabled"] = True
        if loading:
            self._props["aria-busy"] = "true"
        if not _children_present(children):
            self._props["aria-hidden"] = "true"


Placeholder, DbcPlaceholder = make_surface_classes("Placeholder", globals())
placeholder = Placeholder
