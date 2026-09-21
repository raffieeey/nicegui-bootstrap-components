"""Layout family: Container, Row, Col, Stack (native + compat sibling types)."""

from __future__ import annotations

from typing import Any

from .._base import BootstrapElement, UnsupportedPropError, make_surface_classes

__all__ = [
    "Col",
    "Container",
    "DbcCol",
    "DbcContainer",
    "DbcRow",
    "DbcStack",
    "Row",
    "Stack",
    "col",
    "col_breakpoint_classes",
    "container",
    "container_class",
    "row",
    "row_classes",
    "stack",
    "stack_classes",
]

_FLUID_BPS = frozenset({"sm", "md", "lg", "xl", "xxl"})
_ALIGN = frozenset({"start", "center", "end", "stretch", "baseline"})
_JUSTIFY = frozenset({"start", "center", "end", "around", "between", "evenly"})
_STACK_DIRECTIONS = frozenset({"vertical", "horizontal"})
_WIDTH_FRACTIONS = {
    "1/12": 1,
    "1/6": 2,
    "1/4": 3,
    "1/3": 4,
    "5/12": 5,
    "1/2": 6,
    "7/12": 7,
    "2/3": 8,
    "3/4": 9,
    "5/6": 10,
    "11/12": 11,
    "1/1": 12,
    "12/12": 12,
}


def container_class(fluid: bool | str, *, surface: str) -> str:
    """Map ``fluid`` to a Bootstrap container class."""
    if fluid is False:
        return "container"
    if fluid is True:
        return "container-fluid"
    if isinstance(fluid, str):
        if surface == "compat":
            raise UnsupportedPropError("fluid")
        if fluid not in _FLUID_BPS:
            raise ValueError(f"Invalid container fluid breakpoint: {fluid!r}")
        return f"container-{fluid}"
    raise TypeError(f"fluid must be bool or breakpoint str, got {type(fluid)!r}")


def row_classes(
    *,
    align: str | None = None,
    justify: str | None = None,
    g: int | None = None,
    gx: int | None = None,
    gy: int | None = None,
) -> list[str]:
    """Return Bootstrap classes for a Row."""
    classes = ["row"]
    if align is not None:
        if align not in _ALIGN:
            raise ValueError(f"Invalid row align: {align!r}")
        classes.append(f"align-items-{align}")
    if justify is not None:
        if justify not in _JUSTIFY:
            raise ValueError(f"Invalid row justify: {justify!r}")
        classes.append(f"justify-content-{justify}")
    for name, val in (("g", g), ("gx", gx), ("gy", gy)):
        if val is None:
            continue
        if isinstance(val, bool) or not isinstance(val, int) or val < 0 or val > 5:
            raise ValueError(f"{name} must be an int 0-5, got {val!r}")
        classes.append(f"{name}-{val}")
    return classes


def _copied(value: object) -> object:
    if isinstance(value, dict):
        return dict(value)
    return value


def _span_class(n: int, bp: str | None) -> str:
    if bp is None or bp == "xs":
        return f"col-{n}"
    return f"col-{bp}-{n}"


def _check_span(n: int) -> None:
    if n < 1 or n > 12:
        raise ValueError(f"Column size must be 1-12, got {n}")


def _order_classes(order: object, *, bp: str | None) -> list[str]:
    if isinstance(order, str):
        if order not in ("first", "last"):
            raise ValueError(f"order must be 0-12, 'first', or 'last', got {order!r}")
        if bp is None or bp == "xs":
            return [f"order-{order}"]
        return [f"order-{bp}-{order}"]
    if isinstance(order, float):
        raise TypeError("order must not be a float")
    if isinstance(order, bool) or not isinstance(order, int):
        raise TypeError(f"order must be an int, got {type(order)!r}")
    if order < 0 or order > 12:
        raise ValueError(f"order must be 0-12, got {order}")
    if bp is None or bp == "xs":
        return [f"order-{order}"]
    return [f"order-{bp}-{order}"]


def _offset_classes(offset: object, *, bp: str | None) -> list[str]:
    if isinstance(offset, float):
        raise TypeError("offset must not be a float")
    if isinstance(offset, bool) or not isinstance(offset, int):
        raise TypeError(f"offset must be an int, got {type(offset)!r}")
    if offset < 0 or offset > 12:
        raise ValueError(f"offset must be 0-12, got {offset}")
    if bp is None or bp == "xs":
        return [f"offset-{offset}"]
    return [f"offset-{bp}-{offset}"]


def _col_value_to_classes(value: object, *, bp: str | None) -> list[str]:
    if value is None or value is False:
        return []
    if value is True:
        return ["col" if bp in (None, "xs") else f"col-{bp}"]
    if isinstance(value, bool):
        return []
    if isinstance(value, float):
        raise TypeError(
            "Col width/breakpoint values must not be floats; use ints 1-12 or fraction strings"
        )
    if isinstance(value, int):
        _check_span(value)
        return [_span_class(value, bp)]
    if isinstance(value, str):
        if value == "auto":
            return ["col-auto" if bp in (None, "xs") else f"col-{bp}-auto"]
        if value in _WIDTH_FRACTIONS:
            return [_span_class(_WIDTH_FRACTIONS[value], bp)]
        if value.isdigit():
            return _col_value_to_classes(int(value), bp=bp)
        raise ValueError(f"Invalid column size: {value!r}")
    if isinstance(value, dict):
        data = dict(value)
        out: list[str] = []
        if "size" in data:
            out.extend(_col_value_to_classes(data["size"], bp=bp))
        if "order" in data:
            out.extend(_order_classes(data["order"], bp=bp))
        if "offset" in data:
            out.extend(_offset_classes(data["offset"], bp=bp))
        return out
    raise TypeError(f"Unsupported column value type: {type(value)!r}")


def col_breakpoint_classes(
    *,
    width: object = None,
    xs: object = None,
    sm: object = None,
    md: object = None,
    lg: object = None,
    xl: object = None,
    xxl: object = None,
    align: str | None = None,
    order: object = None,
    offset: object = None,
) -> list[str]:
    """Compute Col classes. Caller dicts are copied, not mutated. ``xs`` overrides ``width``."""
    width_v = _copied(width)
    xs_v = _copied(xs)
    sm_v = _copied(sm)
    md_v = _copied(md)
    lg_v = _copied(lg)
    xl_v = _copied(xl)
    xxl_v = _copied(xxl)
    base = xs_v if xs_v is not None else width_v
    classes: list[str] = []
    classes.extend(_col_value_to_classes(base, bp=None))
    if order is not None and not isinstance(base, dict):
        classes.extend(_order_classes(order, bp=None))
    if offset is not None and not isinstance(base, dict):
        classes.extend(_offset_classes(offset, bp=None))
    for bp, val in (("sm", sm_v), ("md", md_v), ("lg", lg_v), ("xl", xl_v), ("xxl", xxl_v)):
        if val is None:
            continue
        classes.extend(_col_value_to_classes(val, bp=bp))
    if align is not None:
        if align not in _ALIGN:
            raise ValueError(f"Invalid col align: {align!r}")
        classes.append(f"align-self-{align}")
    if not classes:
        classes.append("col")
    return classes


def stack_classes(*, direction: str = "vertical", gap: int | None = None) -> list[str]:
    """Return Bootstrap ``vstack``/``hstack`` classes."""
    if direction not in _STACK_DIRECTIONS:
        raise ValueError(f"Invalid stack direction: {direction!r}")
    classes = ["vstack" if direction == "vertical" else "hstack"]
    if gap is not None:
        if isinstance(gap, bool) or not isinstance(gap, int) or gap < 0 or gap > 5:
            raise ValueError(f"gap must be an int 0-5, got {gap!r}")
        classes.append(f"gap-{gap}")
    return classes


class _ContainerImpl(BootstrapElement):
    """Private Container implementation."""

    component_name = "Container"
    children_kind = "auto"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        fluid: bool | str = False,
        tag: str = "div",
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = (container_class(fluid, surface=_surface),)
        super().__init__(children, tag=tag, **kwargs)


class _RowImpl(BootstrapElement):
    """Private Row implementation."""

    component_name = "Row"
    children_kind = "grouping"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        align: str | None = None,
        justify: str | None = None,
        g: int | None = None,
        gx: int | None = None,
        gy: int | None = None,
        tag: str = "div",
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            row_classes(align=align, justify=justify, g=g, gx=gx, gy=gy)
        )
        super().__init__(children, tag=tag, **kwargs)


class _ColImpl(BootstrapElement):
    """Private Col implementation."""

    component_name = "Col"
    children_kind = "auto"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        width: object = None,
        xs: object = None,
        sm: object = None,
        md: object = None,
        lg: object = None,
        xl: object = None,
        xxl: object = None,
        align: str | None = None,
        order: object = None,
        offset: object = None,
        tag: str = "div",
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(
            col_breakpoint_classes(
                width=width,
                xs=xs,
                sm=sm,
                md=md,
                lg=lg,
                xl=xl,
                xxl=xxl,
                align=align,
                order=order,
                offset=offset,
            )
        )
        super().__init__(children, tag=tag, **kwargs)


class _StackImpl(BootstrapElement):
    """Private Stack implementation."""

    component_name = "Stack"
    children_kind = "auto"

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        direction: str = "vertical",
        gap: int | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._structural_classes = tuple(stack_classes(direction=direction, gap=gap))
        super().__init__(children, **kwargs)


Container, DbcContainer = make_surface_classes("Container", globals())
container = Container
Row, DbcRow = make_surface_classes("Row", globals())
row = Row
Col, DbcCol = make_surface_classes("Col", globals())
col = Col
Stack, DbcStack = make_surface_classes("Stack", globals())
stack = Stack
