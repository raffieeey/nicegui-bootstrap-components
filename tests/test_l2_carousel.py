"""L2 tests for the carousel family."""

from __future__ import annotations

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components.bs._carousel import (
    Carousel,
    DbcCarousel,
    carousel,
    carousel_structural_classes,
    clamp_carousel_index,
    normalize_carousel_item,
    resolve_carousel_interval,
    wrap_carousel_index,
)

pytest_plugins = ["nicegui.testing.plugin"]


def _classes_of(element: object) -> list[str]:
    raw = getattr(element, "_classes", [])
    return [str(item) for item in list(raw)]


def _has_class(element: object, name: str) -> bool:
    return name in _classes_of(element)


def _slot_children(element: object) -> list[object]:
    slot = getattr(element, "default_slot", None)
    if slot is None:
        return []
    children = getattr(slot, "children", [])
    return list(children)


def _tag_of(element: object) -> str:
    tag = getattr(element, "tag", None)
    if isinstance(tag, str) and tag:
        return tag
    return str(getattr(element, "_tag", ""))


def _find_child_with_class(element: object, name: str) -> object:
    for child in _slot_children(element):
        if _has_class(child, name):
            return child
    raise AssertionError(f"missing child with class {name!r}")


def test_surfaces_are_distinct() -> None:
    assert Carousel is not DbcCarousel
    assert carousel is Carousel
    assert Carousel.component_name == "Carousel"
    assert DbcCarousel.component_name == "Carousel"


def test_carousel_structural_classes() -> None:
    assert carousel_structural_classes() == ["carousel", "slide"]
    assert carousel_structural_classes(slide=True, variant=None) == ["carousel", "slide"]
    assert carousel_structural_classes(slide=False, variant=None) == ["carousel"]
    assert carousel_structural_classes(slide=True, variant="dark") == [
        "carousel",
        "slide",
        "carousel-dark",
    ]
    assert carousel_structural_classes(slide=False, variant="dark") == [
        "carousel",
        "carousel-dark",
    ]


def test_variant_enum() -> None:
    with pytest.raises(ValueError):
        carousel_structural_classes(variant="light")
    with pytest.raises(ValueError):
        Carousel(items=[], variant="light")


def test_normalize_carousel_item() -> None:
    out = normalize_carousel_item({"src": "a.png", "alt": "A", "unknown": 1, "key": "k"})
    assert out["src"] == "a.png"
    assert out["alt"] == "A"
    assert out["img_class_name"] == "d-block w-100"
    assert "unknown" not in out
    assert "key" not in out
    custom = normalize_carousel_item({"src": "b.png", "img_class_name": "custom"})
    assert custom["img_class_name"] == "custom"


def test_wrap_carousel_index() -> None:
    assert wrap_carousel_index(0, 3) == 0
    assert wrap_carousel_index(1, 3) == 1
    assert wrap_carousel_index(3, 3) == 0
    assert wrap_carousel_index(-1, 3) == 2
    assert wrap_carousel_index(5, 3) == 2
    assert wrap_carousel_index(1, 1) == 0
    assert wrap_carousel_index(-1, 1) == 0
    assert wrap_carousel_index(0, 0) == 0


def test_clamp_carousel_index() -> None:
    assert clamp_carousel_index(1, 3) == 1
    assert clamp_carousel_index(0, 3) == 0
    assert clamp_carousel_index(5, 3) == 0
    assert clamp_carousel_index(-1, 3) == 0
    assert clamp_carousel_index(0, 0) == 0
    assert clamp_carousel_index(2, 2) == 0


def test_resolve_carousel_interval() -> None:
    assert resolve_carousel_interval(None) is None
    assert resolve_carousel_interval(False) is None
    assert resolve_carousel_interval(5000) == 5000
    assert resolve_carousel_interval(0) == 0


def test_items_required() -> None:
    with pytest.raises(TypeError):
        Carousel()


def test_items_must_be_list() -> None:
    with pytest.raises(TypeError):
        Carousel(items={"src": "x.png"})


def test_each_item_must_be_dict() -> None:
    with pytest.raises(TypeError):
        Carousel(items=["nope"])


def test_ride_is_unknown_kwarg() -> None:
    with pytest.raises(TypeError):
        Carousel(items=[], ride="carousel")
    with pytest.raises(TypeError):
        DbcCarousel(items=[], ride=False)


def test_persist_requires_id() -> None:
    with pytest.raises(ValueError):
        Carousel(items=[], persist="local")
    with pytest.raises(ValueError):
        Carousel(items=[], persist="session")


def test_persist_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError):
        Carousel(items=[], persist="memory")


@pytest.mark.user
async def test_carousel_markup_and_caption(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    held: list[Carousel] = []

    @ui.page("/")
    def page() -> None:
        widget = Carousel(
            items=[
                {
                    "src": "slide-a.png",
                    "alt": "A",
                    "header": "Head",
                    "caption": "UniqueCaption42",
                    "bogus": "drop-me",
                },
                {
                    "src": "slide-b.png",
                    "alt": "B",
                    "href": "/next",
                    "target": "_blank",
                },
            ],
            active_index=1,
            controls=True,
            indicators=True,
            variant="dark",
            id="c1",
        )
        held.append(widget)

    await user.open("/")
    await user.should_see("UniqueCaption42")
    widget = held[0]
    assert widget.tag == "div"
    assert _has_class(widget, "carousel")
    assert _has_class(widget, "slide")
    assert _has_class(widget, "carousel-dark")
    assert str(widget._props.get("data-bs-interval", "")).lower() == "false"

    inner = _find_child_with_class(widget, "carousel-inner")
    slides = _slot_children(inner)
    assert len(slides) == 2
    assert not _has_class(slides[0], "active")
    assert _has_class(slides[1], "active")

    first_content = _slot_children(slides[0])
    images = [child for child in first_content if _tag_of(child) == "img"]
    assert images
    assert _has_class(images[0], "d-block")
    assert _has_class(images[0], "w-100")
    captions = [child for child in first_content if _has_class(child, "carousel-caption")]
    assert captions

    second_content = _slot_children(slides[1])
    anchors = [child for child in second_content if _tag_of(child) == "a"]
    assert anchors
    assert str(anchors[0]._props.get("href")) == "/next"
    assert str(anchors[0]._props.get("target")) == "_blank"

    indicators = _find_child_with_class(widget, "carousel-indicators")
    buttons = _slot_children(indicators)
    assert len(buttons) == 2
    assert not _has_class(buttons[0], "active")
    assert _has_class(buttons[1], "active")
    assert str(buttons[0]._props.get("aria-label")) == "Slide 1"
    assert str(buttons[1]._props.get("data-bs-slide-to")) == "1"
    assert str(buttons[1]._props.get("data-bs-target")) == "#c1"

    prev = _find_child_with_class(widget, "carousel-control-prev")
    nxt = _find_child_with_class(widget, "carousel-control-next")
    assert _tag_of(prev) == "button"
    assert _tag_of(nxt) == "button"
    assert str(prev._props.get("data-bs-slide")) == "prev"
    assert str(nxt._props.get("data-bs-slide")) == "next"


@pytest.mark.user
async def test_carousel_empty_without_slide(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    held: list[Carousel] = []

    @ui.page("/")
    def page() -> None:
        widget = Carousel(
            items=[],
            slide=False,
            indicators=True,
            controls=True,
            interval=False,
            active_index=9,
        )
        held.append(widget)

    await user.open("/")
    widget = held[0]
    assert widget.tag == "div"
    assert _has_class(widget, "carousel")
    assert not _has_class(widget, "slide")
    assert widget.active_index == 0
    assert str(widget._props.get("data-bs-interval", "")).lower() == "false"
    assert "data-bs-ride" not in widget._props
    for child in _slot_children(widget):
        assert not _has_class(child, "carousel-indicators")
    inner = _find_child_with_class(widget, "carousel-inner")
    assert _slot_children(inner) == []
    assert _find_child_with_class(widget, "carousel-control-prev")
    assert _find_child_with_class(widget, "carousel-control-next")
