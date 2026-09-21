"""L2 tests for the tooltip and popover family."""

from __future__ import annotations

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components._base import UnsupportedPropError
from nicegui_bootstrap_components.bs._overlay_root import ensure_overlay_root
from nicegui_bootstrap_components.bs._tooltip_popover import (
    DEFAULT_DELAY,
    DEFAULT_POPOVER_AUTOHIDE,
    DEFAULT_POPOVER_FLIP,
    DEFAULT_POPOVER_PLACEMENT,
    DEFAULT_POPOVER_TRIGGER,
    DEFAULT_TOOLTIP_AUTOHIDE,
    DEFAULT_TOOLTIP_FLIP,
    DEFAULT_TOOLTIP_PLACEMENT,
    DEFAULT_TOOLTIP_TRIGGER,
    PLACEMENTS,
    DbcPopover,
    DbcPopoverBody,
    DbcPopoverHeader,
    DbcTooltip,
    Popover,
    PopoverBody,
    PopoverHeader,
    Tooltip,
    normalize_delay,
    normalize_placement,
    normalize_trigger,
    popover,
    popover_body,
    popover_header,
    popover_structural_classes,
    tooltip,
    tooltip_structural_classes,
)

pytest_plugins = ["nicegui.testing.plugin"]


def test_identity_and_class_attrs() -> None:
    assert Tooltip is not DbcTooltip
    assert tooltip is Tooltip
    assert Tooltip.component_name == "Tooltip"
    assert DbcTooltip.component_name == "Tooltip"
    assert Tooltip.children_kind == "phrasing"
    assert Tooltip.reserved_classes == ("tooltip",)

    assert Popover is not DbcPopover
    assert popover is Popover
    assert Popover.component_name == "Popover"
    assert DbcPopover.component_name == "Popover"
    assert Popover.children_kind == "grouping"
    assert Popover.reserved_classes == ("popover",)

    assert PopoverHeader is not DbcPopoverHeader
    assert popover_header is PopoverHeader
    assert PopoverHeader.component_name == "PopoverHeader"
    assert PopoverHeader.children_kind == "phrasing"
    assert PopoverHeader.reserved_classes == ("popover-header",)

    assert PopoverBody is not DbcPopoverBody
    assert popover_body is PopoverBody
    assert PopoverBody.component_name == "PopoverBody"
    assert PopoverBody.children_kind == "auto"
    assert PopoverBody.reserved_classes == ("popover-body",)


def test_documented_defaults() -> None:
    assert DEFAULT_TOOLTIP_PLACEMENT == "auto"
    assert DEFAULT_TOOLTIP_TRIGGER == "hover focus"
    assert DEFAULT_TOOLTIP_AUTOHIDE is True
    assert DEFAULT_TOOLTIP_FLIP is True
    assert DEFAULT_POPOVER_PLACEMENT == "right"
    assert DEFAULT_POPOVER_TRIGGER == "click"
    assert DEFAULT_POPOVER_AUTOHIDE is False
    assert DEFAULT_POPOVER_FLIP is True
    assert DEFAULT_DELAY == {"show": 0, "hide": 50}
    assert normalize_delay(None) == DEFAULT_DELAY
    assert normalize_trigger(None, default=DEFAULT_TOOLTIP_TRIGGER) == "hover focus"
    assert normalize_trigger(None, default=DEFAULT_POPOVER_TRIGGER) == "click"


def test_placement_enum() -> None:
    assert len(PLACEMENTS) == 15
    for value in PLACEMENTS:
        assert normalize_placement(value) == value
    with pytest.raises(ValueError, match="placement"):
        normalize_placement("diagonal")


def test_tooltip_structural_classes() -> None:
    assert tooltip_structural_classes(placement="auto") == [
        "tooltip",
        "bs-tooltip-auto",
        "fade",
    ]
    assert tooltip_structural_classes(placement="top", fade=False) == [
        "tooltip",
        "bs-tooltip-top",
    ]
    assert tooltip_structural_classes(placement="bottom-start") == [
        "tooltip",
        "bs-tooltip-bottom-start",
        "fade",
    ]


def test_popover_structural_classes() -> None:
    assert popover_structural_classes(placement="right") == [
        "popover",
        "bs-popover-right",
        "fade",
    ]
    assert popover_structural_classes(placement="left-end", fade=False) == [
        "popover",
        "bs-popover-left-end",
    ]


def test_all_placements_map_to_classes() -> None:
    for placement in PLACEMENTS:
        assert tooltip_structural_classes(placement=placement, fade=False) == [
            "tooltip",
            f"bs-tooltip-{placement}",
        ]
        assert popover_structural_classes(placement=placement, fade=False) == [
            "popover",
            f"bs-popover-{placement}",
        ]


def test_structural_classes_validate_placement() -> None:
    with pytest.raises(ValueError, match="placement"):
        tooltip_structural_classes(placement="nowhere")
    with pytest.raises(ValueError, match="placement"):
        popover_structural_classes(placement="nowhere")


def test_trigger_validation() -> None:
    assert normalize_trigger("click", default="hover focus") == "click"
    assert normalize_trigger("hover focus click", default="click") == "hover focus click"
    with pytest.raises(ValueError, match="trigger"):
        normalize_trigger("doubletap", default="click")
    with pytest.raises(ValueError, match="trigger"):
        normalize_trigger("   ", default="click")
    with pytest.raises(ValueError, match="trigger"):
        normalize_trigger(1, default="click")  # type: ignore[arg-type]


def test_delay_normalization() -> None:
    assert normalize_delay(200) == {"show": 200, "hide": 200}
    assert normalize_delay({"show": 10, "hide": 20}) == {"show": 10, "hide": 20}
    assert normalize_delay({"show": 5}) == {"show": 5, "hide": 50}
    assert normalize_delay({"hide": 9}) == {"show": 0, "hide": 9}
    with pytest.raises(ValueError, match="delay"):
        normalize_delay(True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="delay"):
        normalize_delay("slow")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="delay"):
        normalize_delay(["nope"])  # type: ignore[arg-type]


def test_tooltip_requires_target() -> None:
    with pytest.raises(ValueError, match="target"):
        Tooltip("hello")
    with pytest.raises(ValueError, match="target"):
        DbcTooltip("hello")
    with pytest.raises(ValueError, match="target"):
        Tooltip("hello", target="")


def test_popover_requires_target() -> None:
    with pytest.raises(ValueError, match="target"):
        Popover()
    with pytest.raises(ValueError, match="target"):
        DbcPopover()
    with pytest.raises(ValueError, match="target"):
        Popover(target="")


def test_invalid_placement_raises_before_construction() -> None:
    with pytest.raises(ValueError, match="placement"):
        Tooltip("x", target="t", placement="north")
    with pytest.raises(ValueError, match="placement"):
        Popover(target="t", placement="south")


def test_invalid_trigger_raises_before_construction() -> None:
    with pytest.raises(ValueError, match="trigger"):
        Tooltip("x", target="t", trigger="tap")
    with pytest.raises(ValueError, match="trigger"):
        Popover(target="t", trigger="swipe")


def test_invalid_offset_raises_before_construction() -> None:
    with pytest.raises(ValueError, match="offset"):
        Popover(target="t", offset=True)
    with pytest.raises(ValueError, match="offset"):
        Popover(target="t", offset=["8"])  # type: ignore[arg-type]


def test_compat_rejects_removed_and_dash_only_props() -> None:
    with pytest.raises(UnsupportedPropError, match="inner_class_name"):
        DbcTooltip("x", target="t", inner_class_name="inner")
    with pytest.raises(UnsupportedPropError, match="innerClassName"):
        DbcPopover(target="t", innerClassName="inner")
    with pytest.raises(UnsupportedPropError, match="external_link"):
        DbcTooltip("x", target="t", external_link=True)
    with pytest.raises(UnsupportedPropError, match="externalLink"):
        DbcPopoverBody("x", externalLink=True)
    with pytest.raises(UnsupportedPropError, match="hide_arrow"):
        DbcTooltip("x", target="t", hide_arrow=True)
    with pytest.raises(UnsupportedPropError, match="offset"):
        DbcTooltip("x", target="t", offset=4)
    with pytest.raises(UnsupportedPropError, match="body"):
        DbcTooltip("x", target="t", body=True)
    with pytest.raises(UnsupportedPropError, match="inner_class_name"):
        DbcPopoverHeader("H", inner_class_name="inner")


@pytest.mark.user
async def test_family_renders_visible_text(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        ui.button("Anchor").props("id=anchor")
        tip = Tooltip("Tip visible", target="anchor", is_open=True)
        assert tip.placement == DEFAULT_TOOLTIP_PLACEMENT
        assert tip.trigger == DEFAULT_TOOLTIP_TRIGGER
        assert tip.autohide is DEFAULT_TOOLTIP_AUTOHIDE
        assert tip.flip is DEFAULT_TOOLTIP_FLIP
        assert tip.delay == DEFAULT_DELAY
        assert tip.tag == "div"
        hdr = PopoverHeader("Hdr")
        body = PopoverBody("Body visible")
        assert hdr.tag == "h3"
        assert body.tag == "div"
        pop = Popover([hdr, body], target="anchor", is_open=True)
        assert pop.placement == DEFAULT_POPOVER_PLACEMENT
        assert pop.trigger == DEFAULT_POPOVER_TRIGGER
        assert pop.autohide is DEFAULT_POPOVER_AUTOHIDE
        assert pop.flip is DEFAULT_POPOVER_FLIP
        assert pop.delay == DEFAULT_DELAY
        assert pop.tag == "div"

    await user.open("/")
    await user.should_see("Tip visible")
    await user.should_see("Hdr")
    await user.should_see("Body visible")


def _overlay_ancestors(element: object) -> list[object]:
    """Walk parent slots upward from an element."""
    ancestors: list[object] = []
    node = element
    for _ in range(8):
        slot = getattr(node, "parent_slot", None)
        node = getattr(slot, "parent", None) if slot else None
        if node is None:
            break
        ancestors.append(node)
    return ancestors


@pytest.mark.user
async def test_tooltip_portals_to_overlay_root(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        ui.button("Anchor").props("id=anchor")
        tip = Tooltip("Tip", target="anchor", is_open=True)
        root = ensure_overlay_root()
        assert root is not None
        assert root in _overlay_ancestors(tip)

    await user.open("/")


@pytest.mark.user
async def test_popover_portals_to_overlay_root(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        ui.button("Anchor").props("id=anchor")
        pop = Popover("Pop", target="anchor", is_open=True)
        root = ensure_overlay_root()
        assert root is not None
        assert root in _overlay_ancestors(pop)

    await user.open("/")
