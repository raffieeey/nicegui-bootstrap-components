"""Shared Bootstrap element contract, dual-surface factory, and normalization."""

from __future__ import annotations

import inspect
import warnings
from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any, Literal, cast

from ._host import (
    Element,
    ValueElement,
    client_store,
    create_text_span,
    get_parent,
    get_slot_parent,
    is_deleted,
    is_ui_element,
    move_element,
    set_element_text,
)

__all__ = [
    "BootstrapElement",
    "BootstrapElementMixin",
    "BootstrapValueElement",
    "ChildrenError",
    "OverlayElement",
    "PropConflictError",
    "SharedProps",
    "UnsupportedPropError",
    "_normalize_children",
    "lookup_public_id",
    "make_surface_classes",
    "normalize_style",
    "prepare_shared_props",
    "reject_or_warn",
    "resolve_class_name",
    "style_to_css",
]

SurfaceName = Literal["native", "compat"]

_UNITLESS = frozenset(
    {
        "animation-iteration-count",
        "flex",
        "flex-grow",
        "flex-shrink",
        "font-weight",
        "line-height",
        "opacity",
        "order",
        "z-index",
        "zoom",
    }
)

_KEY_WARNED = False


class PropConflictError(ValueError):
    """Conflicting aliases that would map to different nodes."""


class ChildrenError(ValueError):
    """Illegal children, adoption, or mixed-content combination."""


class UnsupportedPropError(TypeError):
    """Raised on the compat surface for Dash-only or wrong-surface props."""

    def __init__(self, prop: str, *, component: str | None = None) -> None:
        self.prop = prop
        self.component = component
        if component:
            msg = f"{component}: unsupported prop {prop!r}"
        else:
            msg = f"Unsupported prop {prop!r}"
        super().__init__(msg)


@dataclass(frozen=True)
class SharedProps:
    """Normalized shared constructor fields."""

    public_id: str | None
    class_name: str | None
    style: dict[str, str] | None


def _reset_process_warnings() -> None:
    global _KEY_WARNED
    _KEY_WARNED = False


def _kebab(name: str) -> str:
    if "-" in name:
        return name.lower()
    chars: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            chars.append("-")
        chars.append(ch.lower())
    return "".join(chars)


def normalize_style(style: Mapping[str, Any]) -> dict[str, str]:
    """Px-ify numeric CSS values except the unitless allow-list. Keys are preserved."""
    out: dict[str, str] = {}
    for key, value in style.items():
        if value is None:
            continue
        kebab = _kebab(str(key))
        if isinstance(value, bool):
            out[str(key)] = "true" if value else "false"
            continue
        if isinstance(value, (int, float)) and kebab not in _UNITLESS:
            if isinstance(value, float) and value.is_integer():
                out[str(key)] = f"{int(value)}px"
            else:
                out[str(key)] = f"{value}px"
            continue
        out[str(key)] = str(value)
    return out


def style_to_css(style: Mapping[str, str]) -> str:
    """Serialize a normalized style dict to an inline CSS string."""
    return "; ".join(f"{key}: {value}" for key, value in style.items())


def resolve_class_name(
    class_name: str | None,
    className: str | None,
    surface: str,
) -> str | None:
    """Resolve ``class_name`` / ``className``. ``class_name`` wins when both nonempty."""
    preferred = class_name if class_name else None
    alias = className if className else None
    if preferred and alias:
        if preferred != alias and surface == "native":
            warnings.warn(
                "Both class_name and className were provided; class_name wins. "
                "className is deprecated.",
                DeprecationWarning,
                stacklevel=2,
            )
        return preferred
    return preferred or alias


def reject_or_warn(surface: str, prop: str, *, component: str | None = None) -> None:
    """Raise on compat; warn and ignore on native."""
    if surface == "compat":
        raise UnsupportedPropError(prop, component=component)
    warnings.warn(
        f"{prop} is not supported on the native surface and will be ignored",
        UserWarning,
        stacklevel=3,
    )


def consume_key(surface: str, props: dict[str, Any]) -> None:
    """Drop Dash/React ``key``. Compat raises; native warns once per process."""
    global _KEY_WARNED
    if "key" not in props:
        return
    value = props.pop("key")
    if value is None:
        return
    if surface == "compat":
        raise UnsupportedPropError("key")
    if not _KEY_WARNED:
        _KEY_WARNED = True
        warnings.warn(
            "`key` is unsupported and ignored on the native surface",
            UserWarning,
            stacklevel=3,
        )


def prepare_shared_props(
    surface: str,
    props: dict[str, Any],
    *,
    component: str | None = None,
) -> SharedProps:
    """Pop and normalize shared fields from ``props`` (mutates ``props``)."""
    consume_key(surface, props)
    if "loading_state" in props:
        props.pop("loading_state")
        reject_or_warn(surface, "loading_state", component=component)
    public_id = props.pop("id", None)
    if public_id is not None and not isinstance(public_id, str):
        if isinstance(public_id, (dict, tuple, list)):
            raise TypeError("Pattern-matching ids are not supported")
        public_id = str(public_id)
    class_name = props.pop("class_name", None)
    className = props.pop("className", None)
    style = props.pop("style", None)
    resolved = resolve_class_name(
        class_name if isinstance(class_name, str) or class_name is None else str(class_name),
        className if isinstance(className, str) or className is None else str(className),
        surface,
    )
    if style is None:
        norm_style: dict[str, str] | None = None
    elif isinstance(style, Mapping):
        norm_style = normalize_style(dict(style))
    else:
        raise TypeError(f"style must be a dict, got {type(style)!r}")
    return SharedProps(public_id=public_id, class_name=resolved, style=norm_style)


def _normalize_children(children: object) -> list[object]:
    """Flatten children recursively; drop ``None``; reject unknown types."""
    if children is None:
        return []
    if isinstance(children, bool):
        raise TypeError(f"Unsupported child type: {type(children)!r}")
    if isinstance(children, (str, int, float)) or is_ui_element(children):
        return [children]
    if isinstance(children, (list, tuple)):
        out: list[object] = []
        for child in children:
            out.extend(_normalize_children(child))
        return out
    raise TypeError(f"Unsupported child type: {type(children)!r}")


def _would_cycle(child: Any, new_parent: Any) -> bool:
    if child is new_parent:
        return True
    current: Any | None = new_parent
    seen: set[int] = set()
    while current is not None:
        ident = id(current)
        if ident in seen:
            break
        if current is child:
            return True
        seen.add(ident)
        current = get_parent(current)
    return False


def _to_snake(name: str) -> str:
    out: list[str] = []
    for i, ch in enumerate(name):
        if ch.isupper() and i > 0:
            out.append("_")
        out.append(ch.lower())
    return "".join(out)


def _strip_impl(name: str) -> str:
    trimmed = name[1:] if name.startswith("_") else name
    if trimmed.endswith("Impl"):
        trimmed = trimmed[: -len("Impl")]
    return trimmed


def _make_surface_init(impl_cls: type, surface: str) -> Callable[..., None]:
    impl_init = cast(Any, impl_cls.__init__)  # type: ignore[misc]
    params = list(inspect.signature(impl_init).parameters)
    first = params[1] if len(params) > 1 and params[0] == "self" else (params[0] if params else "")
    value_first = first == "value"

    def __init__(self: Any, children: object = None, *args: Any, **props: Any) -> None:
        init_fn = impl_init
        if value_first:
            init_fn(self, props.pop("value", None), children=children, _surface=surface, **props)
        else:
            init_fn(self, children, _surface=surface, **props)

    __init__.__doc__ = getattr(impl_init, "__doc__", None)
    return __init__


def make_surface_classes(
    impl_name: str | type,
    native_ns: MutableMapping[str, Any] | None = None,
    compat_ns: MutableMapping[str, Any] | None = None,
    component_name: str | None = None,
) -> tuple[type, type]:
    """Create native/compat sibling subclasses of a private impl class.

    ``self._surface`` is set in each public subclass ``__init__`` (via the
    impl's ``_surface`` argument) before shared validation runs.

    When ``impl_name`` is a string, the impl is ``native_ns['_{impl_name}Impl']``.
    The native class is stored under PascalCase and snake_case; the compat
    class is stored as ``Dbc{Name}`` on ``native_ns`` and as ``{Name}`` on
    ``compat_ns`` when provided.
    """
    if isinstance(impl_name, str):
        if native_ns is None:
            raise TypeError("native_ns is required when impl_name is a string")
        name = impl_name
        impl_cls = native_ns[f"_{name}Impl"]
    else:
        impl_cls = impl_name
        name = str(
            component_name
            or getattr(impl_cls, "component_name", None)
            or _strip_impl(impl_cls.__name__)
        )

    native_init = _make_surface_init(impl_cls, "native")
    compat_init = _make_surface_init(impl_cls, "compat")
    native_cls = type(
        name,
        (impl_cls,),
        {
            "__init__": native_init,
            "__module__": impl_cls.__module__,
            "__doc__": impl_cls.__doc__,
            "__qualname__": name,
            "component_name": getattr(impl_cls, "component_name", name),
        },
    )
    compat_cls = type(
        name,
        (impl_cls,),
        {
            "__init__": compat_init,
            "__module__": impl_cls.__module__,
            "__doc__": impl_cls.__doc__,
            "__qualname__": f"Dbc{name}",
            "component_name": getattr(impl_cls, "component_name", name),
        },
    )
    if native_ns is not None:
        native_ns[name] = native_cls
        native_ns[_to_snake(name)] = native_cls
        native_ns[f"Dbc{name}"] = compat_cls
    if compat_ns is not None:
        compat_ns[name] = compat_cls
    return native_cls, compat_cls


def lookup_public_id(public_id: str, *, client: Any | None = None) -> Any | None:
    """Resolve a public (DBC) id via the per-client registry."""
    store = client_store(client)
    registry = store.get("public_ids", {})
    if not isinstance(registry, dict):
        return None
    return registry.get(public_id)


class BootstrapElementMixin:
    """Contract, adoption, public ids, reserved classes. Not an element by itself."""

    component_name: str = ""
    styling_target: str = "root"
    reserved_classes: tuple[str, ...] = ()
    children_kind: str = "auto"
    _surface: str

    def __enter__(self) -> Any:
        if getattr(self, "_children_explicit", False):
            raise ChildrenError(
                "Passing children= is not supported when the element is used as a context manager"
            )
        enter = getattr(super(), "__enter__", None)
        if enter is None:
            return self
        return enter()

    def __exit__(self, *args: Any) -> Any:
        exit_ = getattr(super(), "__exit__", None)
        if exit_ is None:
            return None
        return exit_(*args)

    def _run_bootstrap_init(
        self,
        children: object,
        props: dict[str, Any],
        *,
        init: Callable[[], None],
    ) -> None:
        surface = props.pop("_surface", None)
        if surface is not None:
            self._surface = surface
        elif not hasattr(self, "_surface"):
            self._surface = "native"
        self._ambient_parent = get_slot_parent()
        self._children_explicit = children is not None
        shared = prepare_shared_props(
            self._surface,
            props,
            component=getattr(self, "component_name", None) or None,
        )
        if props:
            raise TypeError(
                f"{self.component_name or type(self).__name__}: unexpected keyword argument(s): "
                + ", ".join(sorted(str(k) for k in props))
            )
        init()
        self._public_id = shared.public_id
        self._user_class_name = shared.class_name
        self._user_style = shared.style
        self._apply_visuals()
        self._set_public_id(self._public_id)
        if children is not None:
            self._adopt(children)
        from .theme import ensure_theme_bound

        ensure_theme_bound()

    def _apply_visuals(self) -> None:
        classes_fn = getattr(self, "classes", None)
        style_fn = getattr(self, "style", None)
        structural = tuple(getattr(self, "_structural_classes", ()))
        if callable(classes_fn):
            for cls in structural:
                if cls:
                    classes_fn(cls)
            # ``reserved_classes`` is a protection set (classes owned by the
            # library that must survive user class mutations); it is never
            # applied eagerly — variants like ``is-invalid`` or
            # ``offcanvas-end`` would otherwise all be added at once.
            user = getattr(self, "_user_class_name", None)
            if user:
                classes_fn(user)
        if callable(style_fn):
            user_style = getattr(self, "_user_style", None)
            if user_style:
                style_fn(style_to_css(user_style))

    def _set_public_id(self, public_id: str | None) -> None:
        self._public_id = public_id
        if not public_id:
            return
        props = getattr(self, "_props", None)
        if props is not None:
            props["data-ngbs-public-id"] = public_id
        try:
            store = client_store(getattr(self, "client", None))
        except Exception:
            return
        registry = store.setdefault("public_ids", {})
        registry[public_id] = self

    def _validate_adoptee(self, child: Any) -> None:
        if is_deleted(child):
            raise ChildrenError("Cannot adopt a deleted element")
        self_client = getattr(self, "client", None)
        child_client = getattr(child, "client", None)
        if self_client is not None and child_client is not None and child_client is not self_client:
            raise ChildrenError("Cannot adopt an element from a different client")
        if _would_cycle(child, self):
            raise ChildrenError("Adopting this element would create a cycle")
        parent = get_parent(child)
        ambient = getattr(self, "_ambient_parent", None)
        if parent is not None and parent is not ambient and parent is not self:
            raise ChildrenError(
                "Cannot steal an element from an unrelated parent; "
                "only nested-expression adoption is allowed"
            )

    def _adopt(self, children: object) -> None:
        items = _normalize_children(children)
        if not items:
            return
        coalesced = _coalesce_children(items)
        grouping = getattr(self, "children_kind", "auto") == "grouping"
        if grouping:
            for item in coalesced:
                if isinstance(item, str):
                    raise ChildrenError(
                        f"{self.component_name}: text children are not allowed. "
                        "Wrap text in a component; this parent only allows element children."
                    )
        text_only = all(isinstance(item, str) for item in coalesced)
        if text_only and coalesced and not grouping:
            set_element_text(self, "".join(coalesced))  # type: ignore[arg-type]
            return
        seen: set[int] = set()
        for item in coalesced:
            if isinstance(item, str):
                span = create_text_span(item)
                move_element(span, self)
                continue
            ident = id(item)
            if ident in seen:
                raise ChildrenError("Duplicate ownership")
            seen.add(ident)
            self._validate_adoptee(item)
            move_element(item, self)


def _coalesce_children(items: list[object]) -> list[object]:
    out: list[object] = []
    buf: list[str] = []
    for item in items:
        if isinstance(item, bool):
            raise TypeError(f"Unsupported child type: {type(item)!r}")
        if isinstance(item, (str, int, float)):
            piece = str(item)
            if piece:
                buf.append(piece)
            continue
        if buf:
            out.append("".join(buf))
            buf = []
        out.append(item)
    if buf:
        out.append("".join(buf))
    return out


class BootstrapElement(BootstrapElementMixin, Element):
    """Structural or hybrid Bootstrap element."""

    def __init__(
        self,
        children: object = None,
        *,
        tag: str = "div",
        id: str | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: Mapping[str, Any] | None = None,
        **compat_props: Any,
    ) -> None:
        if id is not None:
            compat_props.setdefault("id", id)
        if class_name is not None:
            compat_props.setdefault("class_name", class_name)
        if className is not None:
            compat_props.setdefault("className", className)
        if style is not None:
            compat_props.setdefault("style", style)
        self._desired_tag = tag
        self._run_bootstrap_init(
            children,
            compat_props,
            init=lambda: Element.__init__(self, tag),
        )


class BootstrapValueElement(BootstrapElementMixin, ValueElement):
    """Form control with ``.value`` and ``on_change``.

    Frontend contract: accept prop ``model-value`` and emit ``update:modelValue``.
    Inherits NiceGUI ValueElement (bind_value, loopback protection).
    """

    def __init__(
        self,
        children: object = None,
        *,
        value: Any = None,
        on_change: Callable[..., Any] | None = None,
        tag: str = "input",
        id: str | None = None,
        class_name: str | None = None,
        className: str | None = None,
        style: Mapping[str, Any] | None = None,
        **props: Any,
    ) -> None:
        if id is not None:
            props.setdefault("id", id)
        if class_name is not None:
            props.setdefault("class_name", class_name)
        if className is not None:
            props.setdefault("className", className)
        if style is not None:
            props.setdefault("style", style)
        self._desired_tag = tag

        def _init() -> None:
            kwargs: dict[str, Any] = {"value": value}
            if on_change is not None:
                kwargs["on_value_change"] = on_change
            ValueElement.__init__(self, **kwargs)

        self._run_bootstrap_init(children, props, init=_init)


class OverlayElement(BootstrapElement):
    """Desired vs actual visibility; overlay-root registration is opt-in per subclass."""

    uses_overlay_root: bool = True
    is_open: bool = False
    phase: str = "closed"
