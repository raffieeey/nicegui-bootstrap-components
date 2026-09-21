"""Carousel family (native + compat sibling types)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui.element import Element

from .._base import BootstrapElement, make_surface_classes, normalize_style, style_to_css
from .._host import set_element_text

__all__ = [
    "Carousel",
    "DbcCarousel",
    "carousel",
    "carousel_structural_classes",
    "clamp_carousel_index",
    "normalize_carousel_item",
    "resolve_carousel_interval",
    "wrap_carousel_index",
]

_KNOWN_ITEM_KEYS: tuple[str, ...] = (
    "src",
    "alt",
    "header",
    "caption",
    "img_style",
    "img_class_name",
    "caption_class_name",
    "href",
    "target",
    "external_link",
)
_DEFAULT_IMG_CLASS_NAME = "d-block w-100"
_PERSIST_MODES: tuple[str, ...] = ("off", "local", "session")


def carousel_structural_classes(
    *,
    slide: bool = True,
    variant: str | None = None,
) -> list[str]:
    """Return Bootstrap ``carousel`` classes. Unknown variants raise ``ValueError``."""
    if variant is not None and variant != "dark":
        raise ValueError(f"variant must be None or 'dark', got {variant!r}")
    classes = ["carousel"]
    if slide:
        classes.append("slide")
    if variant == "dark":
        classes.append("carousel-dark")
    return classes


def normalize_carousel_item(item: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with known keys only and default ``img_class_name``."""
    normalized: dict[str, Any] = {key: item[key] for key in _KNOWN_ITEM_KEYS if key in item}
    normalized.setdefault("img_class_name", _DEFAULT_IMG_CLASS_NAME)
    return normalized


def wrap_carousel_index(index: int, length: int) -> int:
    """Wrap ``index`` into ``[0, length)``. Empty length yields ``0``."""
    if length <= 0:
        return 0
    return index % length


def clamp_carousel_index(index: int, length: int) -> int:
    """Return ``index`` if in range, otherwise ``0``. Empty length yields ``0``."""
    if length <= 0 or index < 0 or index >= length:
        return 0
    return index


def resolve_carousel_interval(interval: int | bool | None) -> int | None:
    """Return autoplay milliseconds, or ``None`` when autoplay is disabled."""
    if interval is False or interval is None:
        return None
    return int(interval)


def _validate_persist(persist: str, public_id: str | None) -> None:
    if persist not in _PERSIST_MODES:
        raise ValueError(f"persist must be 'off', 'local', or 'session', got {persist!r}")
    if persist != "off" and not public_id:
        raise ValueError("persist requires a public id when not 'off'")


class _CarouselImpl(BootstrapElement):
    """Private Carousel implementation driven by an ``items`` dict list."""

    component_name = "Carousel"
    children_kind = "grouping"
    reserved_classes = ("carousel",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        items: list[dict[str, Any]] | None = None,
        active_index: int = 0,
        controls: bool = True,
        indicators: bool = True,
        interval: int | bool | None = None,
        slide: bool | None = True,
        variant: str | None = None,
        persist: str = "off",
        on_change: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if "ride" in kwargs:
            raise TypeError("Carousel.__init__() got an unexpected keyword argument 'ride'")
        if not isinstance(items, list):
            raise TypeError("items must be a list of dicts")
        for item in items:
            if not isinstance(item, dict):
                raise TypeError("each carousel item must be a dict")

        self._surface = _surface
        raw_id: Any = kwargs.get("id")
        public_id = raw_id if isinstance(raw_id, str) else None
        _validate_persist(persist, public_id)

        slide_enabled = True if slide is None else bool(slide)
        self._structural_classes = tuple(
            carousel_structural_classes(slide=slide_enabled, variant=variant)
        )
        self._items = [normalize_carousel_item(item) for item in items]
        self._active_index = clamp_carousel_index(active_index, len(self._items))
        self._show_controls = bool(controls)
        self._show_indicators = bool(indicators)
        self._on_change = on_change
        self._persist = persist
        self._interval = resolve_carousel_interval(interval)
        self._public_id = public_id
        self._item_elements: list[Element] = []
        self._indicator_elements: list[Element] = []

        super().__init__(None, tag="div", **kwargs)

        if self._interval is None:
            self._props["data-bs-interval"] = "false"
        else:
            self._props["data-bs-interval"] = str(self._interval)
            self._props["data-bs-ride"] = "carousel"

        self._build()

    @property
    def active_index(self) -> int:
        """Zero-based index of the visible slide."""
        return self._active_index

    def _target_selector(self) -> str:
        return f"#{self._public_id}" if self._public_id else ""

    def _build(self) -> None:
        with self:
            self._build_indicators()
            self._build_inner()
            self._build_controls()

    def _build_indicators(self) -> None:
        if not self._show_indicators or not self._items:
            return
        indicators = Element("div")
        indicators.classes("carousel-indicators")
        with indicators:
            for index, _item in enumerate(self._items):
                button = Element("button")
                button._props["type"] = "button"
                button._props["data-bs-target"] = self._target_selector()
                button._props["data-bs-slide-to"] = str(index)
                button._props["aria-label"] = f"Slide {index + 1}"
                if index == self._active_index:
                    button.classes(add="active")
                    button._props["aria-current"] = "true"
                button.on("click", self._make_index_handler(index))
                self._indicator_elements.append(button)

    def _build_inner(self) -> None:
        inner = Element("div")
        inner.classes("carousel-inner")
        with inner:
            for index, item in enumerate(self._items):
                self._build_item(item, is_active=index == self._active_index)

    def _build_item(self, item: dict[str, Any], *, is_active: bool) -> None:
        item_el = Element("div")
        item_el.classes("carousel-item")
        if is_active:
            item_el.classes(add="active")
        with item_el:
            href = item.get("href")
            if href:
                link = Element("a")
                self._apply_link_props(link, item)
                with link:
                    self._add_image(item)
                    self._add_caption(item)
            else:
                self._add_image(item)
                self._add_caption(item)
        self._item_elements.append(item_el)

    def _apply_link_props(self, link: Element, item: dict[str, Any]) -> None:
        link._props["href"] = str(item["href"])
        target = item.get("target")
        if item.get("external_link"):
            link._props["target"] = str(target) if target else "_blank"
            link._props["rel"] = "noopener noreferrer"
        elif target:
            link._props["target"] = str(target)

    def _add_image(self, item: dict[str, Any]) -> None:
        image = Element("img")
        image.classes(str(item.get("img_class_name") or _DEFAULT_IMG_CLASS_NAME))
        src = item.get("src")
        if src is not None:
            image._props["src"] = str(src)
        alt = item.get("alt")
        image._props["alt"] = "" if alt is None else str(alt)
        raw_style = item.get("img_style")
        if raw_style is not None:
            if isinstance(raw_style, dict):
                image.style(style_to_css(normalize_style(raw_style)))
            else:
                image.style(str(raw_style))

    def _add_caption(self, item: dict[str, Any]) -> None:
        header = item.get("header")
        caption = item.get("caption")
        if not header and not caption:
            return
        caption_el = Element("div")
        caption_el.classes("carousel-caption")
        extra = item.get("caption_class_name")
        if extra:
            caption_el.classes(str(extra))
        with caption_el:
            if header:
                heading = Element("h5")
                set_element_text(heading, str(header))
            if caption:
                paragraph = Element("p")
                set_element_text(paragraph, str(caption))

    def _build_controls(self) -> None:
        if not self._show_controls:
            return
        self._build_control("prev")
        self._build_control("next")

    def _build_control(self, direction: str) -> None:
        button = Element("button")
        button.classes(f"carousel-control-{direction}")
        button._props["type"] = "button"
        button._props["data-bs-target"] = self._target_selector()
        button._props["data-bs-slide"] = direction
        with button:
            icon = Element("span")
            icon.classes(f"carousel-control-{direction}-icon")
            icon._props["aria-hidden"] = "true"
            label = Element("span")
            label.classes("visually-hidden")
            set_element_text(label, "Previous" if direction == "prev" else "Next")
        if direction == "prev":
            button.on("click", self._handle_prev)
        else:
            button.on("click", self._handle_next)

    def _make_index_handler(self, index: int) -> Callable[..., None]:
        def _handler(*_args: Any, **_kwargs: Any) -> None:
            self._go_to(index, notify=True)

        return _handler

    def _handle_prev(self, *_args: Any, **_kwargs: Any) -> None:
        self._go_to(wrap_carousel_index(self._active_index - 1, len(self._items)), notify=True)

    def _handle_next(self, *_args: Any, **_kwargs: Any) -> None:
        self._go_to(wrap_carousel_index(self._active_index + 1, len(self._items)), notify=True)

    def _go_to(self, index: int, *, notify: bool) -> None:
        length = len(self._item_elements)
        if length == 0:
            self._active_index = 0
            return
        new_index = wrap_carousel_index(index, length)
        changed = new_index != self._active_index
        self._active_index = new_index
        for i, item_el in enumerate(self._item_elements):
            if i == new_index:
                item_el.classes(add="active")
            else:
                item_el.classes(remove="active")
        for i, indicator_el in enumerate(self._indicator_elements):
            if i == new_index:
                indicator_el.classes(add="active")
                indicator_el._props["aria-current"] = "true"
            else:
                indicator_el.classes(remove="active")
                indicator_el._props["aria-current"] = "false"
        if notify and changed and self._on_change is not None:
            self._on_change()


Carousel, DbcCarousel = make_surface_classes("Carousel", globals())
carousel = Carousel
