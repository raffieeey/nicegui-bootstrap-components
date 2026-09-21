"""Tooltip and Popover family (native + compat sibling types)."""

from __future__ import annotations

from typing import Any

from nicegui.element import Element

from .._base import BootstrapElement, UnsupportedPropError, lookup_public_id, make_surface_classes
from .._host import is_deleted, set_element_text
from ._overlays import _portal_to_overlay_root

__all__ = [
    "Tooltip",
    "DbcTooltip",
    "tooltip",
    "Popover",
    "DbcPopover",
    "popover",
    "PopoverHeader",
    "DbcPopoverHeader",
    "popover_header",
    "PopoverBody",
    "DbcPopoverBody",
    "popover_body",
    "PLACEMENTS",
    "DEFAULT_DELAY",
    "DEFAULT_TOOLTIP_PLACEMENT",
    "DEFAULT_TOOLTIP_TRIGGER",
    "DEFAULT_TOOLTIP_AUTOHIDE",
    "DEFAULT_TOOLTIP_FLIP",
    "DEFAULT_POPOVER_PLACEMENT",
    "DEFAULT_POPOVER_TRIGGER",
    "DEFAULT_POPOVER_AUTOHIDE",
    "DEFAULT_POPOVER_FLIP",
    "normalize_delay",
    "normalize_placement",
    "normalize_trigger",
    "popover_structural_classes",
    "tooltip_structural_classes",
]

PLACEMENTS: tuple[str, ...] = (
    "auto",
    "auto-start",
    "auto-end",
    "top",
    "top-start",
    "top-end",
    "right",
    "right-start",
    "right-end",
    "bottom",
    "bottom-start",
    "bottom-end",
    "left",
    "left-start",
    "left-end",
)
_PLACEMENT_SET: frozenset[str] = frozenset(PLACEMENTS)
_TRIGGER_TOKENS: frozenset[str] = frozenset({"hover", "focus", "click", "manual"})

DEFAULT_DELAY: dict[str, int] = {"show": 0, "hide": 50}
DEFAULT_TOOLTIP_PLACEMENT = "auto"
DEFAULT_TOOLTIP_TRIGGER = "hover focus"
DEFAULT_TOOLTIP_AUTOHIDE = True
DEFAULT_TOOLTIP_FLIP = True
DEFAULT_POPOVER_PLACEMENT = "right"
DEFAULT_POPOVER_TRIGGER = "click"
DEFAULT_POPOVER_AUTOHIDE = False
DEFAULT_POPOVER_FLIP = True

_COMPAT_REJECT: tuple[str, ...] = (
    "inner_class_name",
    "innerClassName",
    "external_link",
    "externalLink",
)


def normalize_placement(placement: str) -> str:
    """Return a validated Bootstrap placement value."""
    if placement not in _PLACEMENT_SET:
        raise ValueError(f"Unknown placement {placement!r}")
    return placement


def normalize_trigger(trigger: str | None, *, default: str) -> str:
    """Return a validated space-separated trigger list."""
    if trigger is None:
        return default
    if not isinstance(trigger, str):
        raise ValueError(f"Unknown trigger {trigger!r}")
    tokens = [token for token in trigger.split() if token]
    if not tokens:
        raise ValueError("trigger must be a non-empty space-separated list")
    for token in tokens:
        if token not in _TRIGGER_TOKENS:
            raise ValueError(f"Unknown trigger {token!r}")
    return " ".join(tokens)


def normalize_delay(delay: dict[str, Any] | int | None) -> dict[str, int]:
    """Return a ``{show, hide}`` delay map. ``None`` uses DBC defaults."""
    if delay is None:
        return {"show": DEFAULT_DELAY["show"], "hide": DEFAULT_DELAY["hide"]}
    if isinstance(delay, bool):
        raise ValueError("delay must be an int or a dict with show/hide keys")
    if isinstance(delay, int):
        value = int(delay)
        return {"show": value, "hide": value}
    if isinstance(delay, dict):
        show_raw: Any = delay.get("show", 0)
        hide_raw: Any = delay.get("hide", 50)
        if show_raw is None:
            show_raw = 0
        if hide_raw is None:
            hide_raw = 50
        try:
            return {"show": int(show_raw), "hide": int(hide_raw)}
        except (TypeError, ValueError) as exc:
            raise ValueError("delay must be an int or a dict with show/hide keys") from exc
    raise ValueError("delay must be an int or a dict with show/hide keys")


def tooltip_structural_classes(*, placement: str, fade: bool = True) -> list[str]:
    """Return Bootstrap ``tooltip`` classes. Unknown placements raise ``ValueError``."""
    placement = normalize_placement(placement)
    classes = ["tooltip", f"bs-tooltip-{placement}"]
    if fade:
        classes.append("fade")
    return classes


def popover_structural_classes(*, placement: str, fade: bool = True) -> list[str]:
    """Return Bootstrap ``popover`` classes. Unknown placements raise ``ValueError``."""
    placement = normalize_placement(placement)
    classes = ["popover", f"bs-popover-{placement}"]
    if fade:
        classes.append("fade")
    return classes


def _reject_compat_only_props(
    surface: str,
    kwargs: dict[str, Any],
    extra: tuple[str, ...] = (),
) -> None:
    """Reject removed or native-only props on the compat surface."""
    for name in (*_COMPAT_REJECT, *extra):
        if name not in kwargs:
            continue
        del kwargs[name]
        if surface == "compat":
            raise UnsupportedPropError(name)


def _consume_passthrough_props(kwargs: dict[str, Any]) -> tuple[Any, Any]:
    """Remove Dash runtime extras that must not become DOM attributes."""
    for name in ("key", "loading_state", "loadingState"):
        kwargs.pop(name, None)
    overlay_style = kwargs.pop("overlay_style", None)
    popper_parameters = kwargs.pop("popper_parameters", None)
    return overlay_style, popper_parameters


def _require_target(component_name: str, target: object) -> str | Any:
    """Require a non-empty target id or element reference."""
    if isinstance(target, str):
        if target == "":
            raise ValueError(f"{component_name} requires a target")
        return target
    if target is None:
        raise ValueError(f"{component_name} requires a target")
    return target


def _normalize_offset(offset: str | int | float | None) -> str | int | None:
    """Return a Popover offset value."""
    if offset is None:
        return None
    if isinstance(offset, bool):
        raise ValueError("offset must be a string or number")
    if isinstance(offset, str):
        return offset
    if isinstance(offset, (int, float)):
        return int(offset)
    raise ValueError("offset must be a string or number")


def _assign_plain_children(element: Any, children: object) -> None:
    """Render children into a plain NiceGUI element without HTML injection."""
    if children is None:
        return
    if isinstance(children, (list, tuple)):
        if not children:
            return
        if all(isinstance(child, (str, int, float)) for child in children):
            set_element_text(element, "".join(str(child) for child in children))
            return
        for child in children:
            _assign_plain_children(element, child)
        return
    if isinstance(children, (str, int, float)):
        set_element_text(element, str(children))
        return
    mover = getattr(children, "move", None)
    if callable(mover):
        mover(element)


def _target_html_id(target: str | Any) -> str:
    if isinstance(target, str):
        return target
    props = getattr(target, "_props", None)
    if isinstance(props, dict) and props.get("id"):
        return str(props.get("id"))
    return ""


def _anchor_javascript(vue_id: object, html_id: object, target_id: str, placement: str) -> str:
    return (
        "(function(){"
        f"var placement={placement!r};"
        f"var targetId={target_id!r};"
        f"var vueId={vue_id!r};"
        f"var htmlId={html_id!r};"
        "var el=null;"
        "if(htmlId){el=document.getElementById(String(htmlId));}"
        "try{if(!el && typeof getElement==='function'){el=getElement(vueId);}}catch(e){}"
        "if(!el){return;}"
        "var target=targetId?document.getElementById(targetId):null;"
        "if(!target){return;}"
        "var t=target.getBoundingClientRect();"
        "var r=el.getBoundingClientRect();"
        "var gap=8;"
        "var base=String(placement).split('-')[0];"
        "var top=t.bottom+gap;"
        "var left=t.left+(t.width-r.width)/2;"
        "if(base==='top'){top=t.top-r.height-gap;}"
        "else if(base==='left'){top=t.top+(t.height-r.height)/2;left=t.left-r.width-gap;}"
        "else if(base==='right'){top=t.top+(t.height-r.height)/2;left=t.right+gap;}"
        "el.style.position='fixed';"
        "el.style.zIndex='5090';"
        "el.style.top=Math.max(0,top)+'px';"
        "el.style.left=Math.max(0,left)+'px';"
        "})();"
    )


def _position_to_target(overlay: Any) -> None:
    """Anchor the overlay using the target bounding rect when a client is available."""
    if not bool(getattr(overlay, "is_open", False)):
        return
    client = getattr(overlay, "client", None)
    if client is None:
        return
    run_js = getattr(client, "run_javascript", None)
    if not callable(run_js):
        return
    target = getattr(overlay, "target", None)
    target_id = _target_html_id(target)
    props = getattr(overlay, "_props", None)
    html_id: object = None
    if isinstance(props, dict):
        html_id = props.get("id")
    script = _anchor_javascript(
        getattr(overlay, "id", None),
        html_id,
        target_id,
        str(getattr(overlay, "placement", "auto")),
    )
    try:
        run_js(script)
    except Exception:
        return


def _apply_open_state(overlay: Any, open_: bool) -> None:
    """Toggle the Bootstrap ``show`` class and aria-hidden flag."""
    overlay.is_open = open_
    if open_:
        overlay.classes(add="show")
    else:
        overlay.classes(remove="show")
    overlay._props["aria-hidden"] = "false" if open_ else "true"
    if open_:
        _position_to_target(overlay)


def _bind_trigger_listeners(
    overlay: Any,
    target: str | Any,
    trigger: str,
    *,
    autohide: bool,
) -> None:
    """Register open/close listeners on the target. Called from ``__init__`` only."""
    resolved: Any = target
    if isinstance(target, str):
        try:
            resolved = lookup_public_id(target)
        except Exception:
            return
        if resolved is None:
            return
    if resolved is overlay:
        return
    on = getattr(resolved, "on", None)
    if not callable(on):
        return
    tokens = set(trigger.split())

    def handle_open(*_args: Any, **_kwargs: Any) -> None:
        if is_deleted(overlay):
            return
        if not isinstance(target, str) and is_deleted(target):
            _apply_open_state(overlay, False)
            return
        _apply_open_state(overlay, True)

    def handle_close(*_args: Any, **_kwargs: Any) -> None:
        if is_deleted(overlay):
            return
        if autohide:
            _apply_open_state(overlay, False)

    def handle_toggle(*_args: Any, **_kwargs: Any) -> None:
        if is_deleted(overlay):
            return
        if not isinstance(target, str) and is_deleted(target):
            _apply_open_state(overlay, False)
            return
        _apply_open_state(overlay, not bool(getattr(overlay, "is_open", False)))

    if "hover" in tokens:
        resolved.on("mouseenter", handle_open)
        resolved.on("mouseleave", handle_close)
    if "focus" in tokens:
        resolved.on("focus", handle_open)
        resolved.on("blur", handle_close)
    if "click" in tokens:
        resolved.on("click", handle_toggle)


def _apply_overlay_chrome(
    overlay: Any,
    *,
    placement: str,
    target: str | Any,
    is_open: bool | None,
) -> None:
    overlay._props["role"] = "tooltip"
    overlay._props["data-bs-placement"] = placement
    overlay._props["aria-hidden"] = "false" if is_open else "true"
    if isinstance(target, str):
        overlay._props["data-bs-target"] = target


class _TooltipImpl(BootstrapElement):
    """Private Tooltip implementation."""

    component_name = "Tooltip"
    children_kind = "phrasing"
    reserved_classes = ("tooltip",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        target: str | Any | None = None,
        placement: str = DEFAULT_TOOLTIP_PLACEMENT,
        trigger: str | None = None,
        delay: dict[str, Any] | int | None = None,
        is_open: bool | None = None,
        autohide: bool = DEFAULT_TOOLTIP_AUTOHIDE,
        fade: bool = True,
        flip: bool = DEFAULT_TOOLTIP_FLIP,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        _reject_compat_only_props(_surface, kwargs, extra=("hide_arrow", "offset", "body"))
        overlay_style, popper_parameters = _consume_passthrough_props(kwargs)
        self.target = _require_target(self.component_name, target)
        self.placement = normalize_placement(placement)
        self.trigger = normalize_trigger(trigger, default=DEFAULT_TOOLTIP_TRIGGER)
        self.delay = normalize_delay(delay)
        self.is_open = is_open
        self.autohide = bool(autohide)
        self.fade = bool(fade)
        self.flip = bool(flip)
        self.overlay_style = overlay_style
        self.popper_parameters = popper_parameters
        classes = tooltip_structural_classes(placement=self.placement, fade=self.fade)
        if self.is_open:
            classes.append("show")
        self._structural_classes = tuple(classes)
        super().__init__(None, tag="div", **kwargs)
        _portal_to_overlay_root(self)
        _apply_overlay_chrome(
            self, placement=self.placement, target=self.target, is_open=self.is_open
        )
        with self:
            arrow = Element("div")
            arrow.classes("tooltip-arrow")
            inner = Element("div")
            inner.classes("tooltip-inner")
            _assign_plain_children(inner, children)
        self._inner = inner
        _bind_trigger_listeners(self, self.target, self.trigger, autohide=self.autohide)
        if self.is_open:
            _position_to_target(self)


Tooltip, DbcTooltip = make_surface_classes("Tooltip", globals())
tooltip = Tooltip


class _PopoverHeaderImpl(BootstrapElement):
    """Private PopoverHeader implementation."""

    component_name = "PopoverHeader"
    children_kind = "phrasing"
    reserved_classes = ("popover-header",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        _reject_compat_only_props(_surface, kwargs)
        self._structural_classes = ("popover-header",)
        super().__init__(children, tag="h3", **kwargs)


PopoverHeader, DbcPopoverHeader = make_surface_classes("PopoverHeader", globals())
popover_header = PopoverHeader


class _PopoverBodyImpl(BootstrapElement):
    """Private PopoverBody implementation."""

    component_name = "PopoverBody"
    children_kind = "auto"
    reserved_classes = ("popover-body",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        _reject_compat_only_props(_surface, kwargs)
        self._structural_classes = ("popover-body",)
        super().__init__(children, tag="div", **kwargs)


PopoverBody, DbcPopoverBody = make_surface_classes("PopoverBody", globals())
popover_body = PopoverBody


class _PopoverImpl(BootstrapElement):
    """Private Popover implementation.

    Bootstrap 5.3 exposes popovers with ``role="tooltip"`` even when the
    overlay contains richer header/body content. Interactive descendants are a
    known Bootstrap limitation.
    """

    component_name = "Popover"
    children_kind = "grouping"
    reserved_classes = ("popover",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        target: str | Any | None = None,
        placement: str = DEFAULT_POPOVER_PLACEMENT,
        trigger: str | None = None,
        delay: dict[str, Any] | int | None = None,
        is_open: bool | None = None,
        autohide: bool = DEFAULT_POPOVER_AUTOHIDE,
        fade: bool = True,
        flip: bool = DEFAULT_POPOVER_FLIP,
        hide_arrow: bool = False,
        offset: str | int | float | None = None,
        body: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        _reject_compat_only_props(_surface, kwargs)
        overlay_style, popper_parameters = _consume_passthrough_props(kwargs)
        self.target = _require_target(self.component_name, target)
        self.placement = normalize_placement(placement)
        self.trigger = normalize_trigger(trigger, default=DEFAULT_POPOVER_TRIGGER)
        self.delay = normalize_delay(delay)
        self.is_open = is_open
        self.autohide = bool(autohide)
        self.fade = bool(fade)
        self.flip = bool(flip)
        self.hide_arrow = bool(hide_arrow)
        self.offset = _normalize_offset(offset)
        self.body = bool(body)
        self.overlay_style = overlay_style
        self.popper_parameters = popper_parameters
        classes = popover_structural_classes(placement=self.placement, fade=self.fade)
        if self.is_open:
            classes.append("show")
        self._structural_classes = tuple(classes)
        super().__init__(None, tag="div", **kwargs)
        _portal_to_overlay_root(self)
        _apply_overlay_chrome(
            self, placement=self.placement, target=self.target, is_open=self.is_open
        )
        arrow: Element | None = None
        with self:
            _assign_plain_children(self, children)
            if not self.hide_arrow:
                arrow = Element("div")
                arrow.classes("popover-arrow")
        if arrow is not None:
            arrow.move(target_container=self, target_index=0)
        _bind_trigger_listeners(self, self.target, self.trigger, autohide=self.autohide)
        if self.is_open:
            _position_to_target(self)


Popover, DbcPopover = make_surface_classes("Popover", globals())
popover = Popover
