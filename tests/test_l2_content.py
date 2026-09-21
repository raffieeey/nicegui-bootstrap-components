"""L2 tests for the content, list-group and table families."""

from __future__ import annotations

import inspect
import sys
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components._base import PropConflictError, UnsupportedPropError
from nicegui_bootstrap_components.bs._content import (
    Badge,
    Card,
    CardBody,
    CardFooter,
    CardGroup,
    CardHeader,
    CardImg,
    CardImgOverlay,
    CardLink,
    DbcBadge,
    DbcCard,
    DbcCardBody,
    DbcCardFooter,
    DbcCardGroup,
    DbcCardHeader,
    DbcCardImg,
    DbcCardImgOverlay,
    DbcCardLink,
    DbcListGroup,
    DbcListGroupItem,
    DbcPlaceholder,
    DbcProgress,
    DbcTable,
    ListGroup,
    ListGroupItem,
    Placeholder,
    Progress,
    Table,
    badge,
    badge_structural_classes,
    card,
    card_body,
    card_footer,
    card_group,
    card_header,
    card_img,
    card_img_overlay,
    card_img_structural_classes,
    card_link,
    card_structural_classes,
    format_table_cell,
    grouped_spans,
    list_group,
    list_group_item,
    list_group_item_structural_classes,
    list_group_structural_classes,
    placeholder,
    placeholder_structural_classes,
    progress,
    progress_bar_structural_classes,
    progress_percent,
    progress_structural_classes,
    resolve_list_group_item_tag,
    resolve_list_group_tag,
    table,
    table_responsive_class,
    table_structural_classes,
)

pytest_plugins = ["nicegui.testing.plugin"]

_SURFACE_CASES = [
    (Card, DbcCard, card, "Card"),
    (CardBody, DbcCardBody, card_body, "CardBody"),
    (CardHeader, DbcCardHeader, card_header, "CardHeader"),
    (CardFooter, DbcCardFooter, card_footer, "CardFooter"),
    (CardGroup, DbcCardGroup, card_group, "CardGroup"),
    (CardImg, DbcCardImg, card_img, "CardImg"),
    (CardImgOverlay, DbcCardImgOverlay, card_img_overlay, "CardImgOverlay"),
    (CardLink, DbcCardLink, card_link, "CardLink"),
    (ListGroup, DbcListGroup, list_group, "ListGroup"),
    (ListGroupItem, DbcListGroupItem, list_group_item, "ListGroupItem"),
    (Table, DbcTable, table, "Table"),
    (Badge, DbcBadge, badge, "Badge"),
    (Progress, DbcProgress, progress, "Progress"),
    (Placeholder, DbcPlaceholder, placeholder, "Placeholder"),
]


@pytest.mark.parametrize(("native", "compat", "alias", "name"), _SURFACE_CASES)
def test_surface_identity(
    native: type[Any], compat: type[Any], alias: type[Any], name: str
) -> None:
    assert native is not compat
    assert alias is native
    assert native.component_name == name
    assert compat.component_name == name


def test_children_kinds() -> None:
    assert Card.children_kind == "auto"
    assert CardBody.children_kind == "auto"
    assert CardHeader.children_kind == "auto"
    assert CardFooter.children_kind == "auto"
    assert CardImgOverlay.children_kind == "auto"
    assert ListGroupItem.children_kind == "auto"
    assert Progress.children_kind == "auto"
    assert Placeholder.children_kind == "auto"
    assert CardImg.children_kind == "auto"
    assert CardGroup.children_kind == "grouping"
    assert ListGroup.children_kind == "grouping"
    assert Table.children_kind == "grouping"
    assert Badge.children_kind == "phrasing"
    assert CardLink.children_kind == "phrasing"


def test_card_structural_classes_default() -> None:
    assert card_structural_classes() == ["card"]


def test_card_structural_classes_body() -> None:
    assert card_structural_classes(body=True) == ["card", "card-body"]


def test_card_structural_classes_color() -> None:
    assert card_structural_classes(color="primary") == ["card", "text-bg-primary"]


def test_card_structural_classes_outline() -> None:
    assert card_structural_classes(color="primary", outline=True) == [
        "card",
        "border-primary",
    ]


def test_card_structural_classes_inverse() -> None:
    assert card_structural_classes(inverse=True) == ["card", "text-white"]


def test_card_structural_classes_combined() -> None:
    assert card_structural_classes(color="info", outline=True, inverse=True, body=True) == [
        "card",
        "card-body",
        "border-info",
        "text-white",
    ]


def test_card_does_not_insert_body_by_default() -> None:
    assert "card-body" not in card_structural_classes()
    assert "card-body" not in card_structural_classes(color="secondary")


def test_card_img_structural_classes() -> None:
    assert card_img_structural_classes() == ["card-img"]
    assert card_img_structural_classes(overlay=True) == ["card-img"]
    assert card_img_structural_classes(top=True) == ["card-img-top"]
    assert card_img_structural_classes(bottom=True) == ["card-img-bottom"]


def test_card_img_position_conflicts() -> None:
    with pytest.raises(PropConflictError):
        card_img_structural_classes(top=True, bottom=True)
    with pytest.raises(PropConflictError):
        card_img_structural_classes(top=True, overlay=True)
    with pytest.raises(PropConflictError):
        card_img_structural_classes(bottom=True, overlay=True)
    with pytest.raises(PropConflictError):
        CardImg(top=True, bottom=True)
    with pytest.raises(PropConflictError):
        CardImg(top=True, overlay=True)


def test_list_group_structural_classes() -> None:
    assert list_group_structural_classes() == ["list-group"]
    assert list_group_structural_classes(flush=True) == ["list-group", "list-group-flush"]
    assert list_group_structural_classes(numbered=True) == [
        "list-group",
        "list-group-numbered",
    ]
    assert list_group_structural_classes(horizontal=True) == [
        "list-group",
        "list-group-horizontal",
    ]
    assert list_group_structural_classes(horizontal="md") == [
        "list-group",
        "list-group-horizontal-md",
    ]
    assert list_group_structural_classes(flush=True, numbered=True, horizontal="xl") == [
        "list-group",
        "list-group-flush",
        "list-group-numbered",
        "list-group-horizontal-xl",
    ]


def test_list_group_unknown_horizontal() -> None:
    with pytest.raises(ValueError, match="Unknown horizontal breakpoint"):
        list_group_structural_classes(horizontal="xs")
    with pytest.raises(ValueError, match="Unknown horizontal breakpoint"):
        ListGroup(horizontal="huge")


def test_resolve_list_group_tag() -> None:
    assert resolve_list_group_tag() == "div"
    assert resolve_list_group_tag(numbered=True) == "ol"
    assert resolve_list_group_tag(tag="ul", numbered=True) == "ul"
    assert resolve_list_group_tag(tag="ol") == "ol"
    assert resolve_list_group_tag(tag="div", numbered=True) == "div"


def test_list_group_item_structural_classes() -> None:
    assert list_group_item_structural_classes() == ["list-group-item"]
    assert list_group_item_structural_classes(active=True) == [
        "list-group-item",
        "active",
    ]
    assert list_group_item_structural_classes(disabled=True) == [
        "list-group-item",
        "disabled",
    ]
    assert list_group_item_structural_classes(action=True) == [
        "list-group-item",
        "list-group-item-action",
    ]
    assert list_group_item_structural_classes(href="#") == [
        "list-group-item",
        "list-group-item-action",
    ]
    assert list_group_item_structural_classes(color="info") == [
        "list-group-item",
        "list-group-item-info",
    ]
    assert list_group_item_structural_classes(
        color="primary", action=True, active=True, disabled=True
    ) == [
        "list-group-item",
        "list-group-item-primary",
        "list-group-item-action",
        "active",
        "disabled",
    ]


def test_resolve_list_group_item_tag() -> None:
    assert resolve_list_group_item_tag() == "div"
    assert resolve_list_group_item_tag(href="#") == "a"
    assert resolve_list_group_item_tag(action=True) == "button"
    assert resolve_list_group_item_tag(tag="li", href="#", action=True) == "li"
    assert resolve_list_group_item_tag(href="#", action=True) == "a"
    assert resolve_list_group_item_tag(action=True, context_default="li") == "button"
    assert resolve_list_group_item_tag(context_default="li") == "li"
    assert resolve_list_group_item_tag(context_default="div") == "div"


def test_table_structural_classes() -> None:
    assert table_structural_classes() == ["table"]
    assert table_structural_classes(bordered=True) == ["table", "table-bordered"]
    assert table_structural_classes(borderless=True) == ["table", "table-borderless"]
    assert table_structural_classes(striped=True) == ["table", "table-striped"]
    assert table_structural_classes(hover=True) == ["table", "table-hover"]
    assert table_structural_classes(small=True) == ["table", "table-sm"]
    assert table_structural_classes(size="sm") == ["table", "table-sm"]
    assert table_structural_classes(small=True, size="sm") == ["table", "table-sm"]
    assert table_structural_classes(color="info") == ["table", "table-info"]
    assert table_structural_classes(striped_columns=True) == [
        "table",
        "table-striped-columns",
    ]
    assert table_structural_classes(
        bordered=True,
        striped=True,
        hover=True,
        size="sm",
        color="dark",
        striped_columns=True,
    ) == [
        "table",
        "table-bordered",
        "table-striped",
        "table-striped-columns",
        "table-hover",
        "table-sm",
        "table-dark",
    ]


def test_table_border_conflict() -> None:
    with pytest.raises(PropConflictError):
        table_structural_classes(bordered=True, borderless=True)
    with pytest.raises(PropConflictError):
        Table(bordered=True, borderless=True)


def test_table_small_size_conflict() -> None:
    with pytest.raises(PropConflictError):
        table_structural_classes(small=True, size="lg")


def test_table_unknown_size() -> None:
    with pytest.raises(ValueError, match="Unknown table size"):
        table_structural_classes(size="lg")
    with pytest.raises(ValueError, match="Unknown table size"):
        Table(size="lg")


def test_table_responsive_class() -> None:
    assert table_responsive_class(False) is None
    assert table_responsive_class(True) == "table-responsive"
    assert table_responsive_class("sm") == "table-responsive-sm"
    assert table_responsive_class("xxl") == "table-responsive-xxl"


def test_table_unknown_responsive() -> None:
    with pytest.raises(ValueError, match="Unknown responsive breakpoint"):
        table_responsive_class("xs")
    with pytest.raises(ValueError, match="Unknown responsive breakpoint"):
        Table(responsive="huge")


def test_dbc_table_rejects_dark() -> None:
    with pytest.raises(UnsupportedPropError):
        DbcTable(dark=True)
    with pytest.raises(UnsupportedPropError):
        DbcTable(dark=False)


def test_native_table_rejects_dark() -> None:
    with pytest.raises(ValueError, match="dark"):
        Table(dark=True)


def test_dbc_table_rejects_small() -> None:
    with pytest.raises(UnsupportedPropError):
        DbcTable(small=True)


def test_from_dataframe_signature_defaults() -> None:
    params = inspect.signature(Table.from_dataframe).parameters
    assert params["header"].default is True
    assert params["index"].default is True
    assert params["columns"].default is None
    assert params["index_label"].default is None
    assert params["date_format"].default is None
    assert params["float_format"].default is None
    assert params["caption"].default is None


def test_from_dataframe_missing_pandas(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "pandas", None)
    with pytest.raises(ImportError, match="pandas"):
        Table.from_dataframe({})


def test_grouped_spans() -> None:
    assert grouped_spans([]) == []
    assert grouped_spans(["x"]) == [("x", 1)]
    assert grouped_spans(["a", "a", "b"]) == [("a", 2), ("b", 1)]
    assert grouped_spans([1, 1, 1, 2, 2]) == [(1, 3), (2, 2)]


def test_format_table_cell() -> None:
    assert format_table_cell(None) == ""
    assert format_table_cell("x") == "x"
    assert format_table_cell(3) == "3"
    assert format_table_cell(1.26, float_format="%.1f") == "1.3"
    assert format_table_cell(1.2, float_format=".2f") == "1.20"
    assert format_table_cell(1.5, float_format=lambda v: f"{v:.0f}") == "2"
    assert format_table_cell(date(2020, 1, 2), date_format="%Y-%m-%d") == "2020-01-02"
    assert format_table_cell(datetime(2020, 1, 2, 3, 4), date_format="%H") == "03"
    assert format_table_cell(("a", "b")) == "a b"
    assert format_table_cell(True) == "True"


def test_badge_structural_classes() -> None:
    assert badge_structural_classes() == ["badge", "text-bg-secondary"]
    assert badge_structural_classes(color="primary") == ["badge", "text-bg-primary"]
    assert badge_structural_classes(pill=True) == [
        "badge",
        "text-bg-secondary",
        "rounded-pill",
    ]
    assert badge_structural_classes(color="danger", text_color="white", pill=True) == [
        "badge",
        "text-bg-danger",
        "text-white",
        "rounded-pill",
    ]


def test_badge_unknown_text_color() -> None:
    with pytest.raises(ValueError, match="Unknown color"):
        badge_structural_classes(text_color="nope")
    with pytest.raises(ValueError, match="Unknown color"):
        Badge(text_color="nope")


def test_progress_structural_classes() -> None:
    assert progress_structural_classes() == ["progress"]


def test_progress_bar_structural_classes() -> None:
    assert progress_bar_structural_classes() == ["progress-bar"]
    assert progress_bar_structural_classes(color="success") == [
        "progress-bar",
        "bg-success",
    ]
    assert progress_bar_structural_classes(striped=True) == [
        "progress-bar",
        "progress-bar-striped",
    ]
    assert progress_bar_structural_classes(animated=True) == [
        "progress-bar",
        "progress-bar-striped",
        "progress-bar-animated",
    ]
    assert progress_bar_structural_classes(color="warning", striped=True, animated=True) == [
        "progress-bar",
        "bg-warning",
        "progress-bar-striped",
        "progress-bar-animated",
    ]


def test_progress_percent() -> None:
    assert progress_percent(50, 0, 100) == 50.0
    assert progress_percent(0, 0, 100) == 0.0
    assert progress_percent(100, 0, 100) == 100.0
    assert progress_percent(50, 0, 0) == 0.0
    assert progress_percent(-10, 0, 100) == 0.0
    assert progress_percent(150, 0, 100) == 100.0
    assert progress_percent(20, 10, 30) == 50.0


def test_placeholder_structural_classes() -> None:
    assert placeholder_structural_classes() == ["placeholder"]
    assert placeholder_structural_classes(animation="glow") == [
        "placeholder",
        "placeholder-glow",
    ]
    assert placeholder_structural_classes(animation="wave") == [
        "placeholder",
        "placeholder-wave",
    ]
    assert placeholder_structural_classes(size="lg") == ["placeholder", "placeholder-lg"]
    assert placeholder_structural_classes(size="xs") == ["placeholder", "placeholder-xs"]
    assert placeholder_structural_classes(color="primary") == [
        "placeholder",
        "bg-primary",
    ]
    assert placeholder_structural_classes(button=True, color="primary") == [
        "placeholder",
        "btn",
        "disabled",
        "btn-primary",
    ]
    assert placeholder_structural_classes(xs=6) == ["placeholder", "col-6"]
    assert placeholder_structural_classes(xs=True) == ["placeholder", "col"]
    assert placeholder_structural_classes(sm=True) == ["placeholder", "col-sm"]
    assert placeholder_structural_classes(sm=6) == ["placeholder", "col-sm-6"]
    assert placeholder_structural_classes(width=50) == ["placeholder", "w-50"]
    assert placeholder_structural_classes(width=4) == ["placeholder", "col-4"]
    assert placeholder_structural_classes(display=False) == ["placeholder", "d-none"]
    assert placeholder_structural_classes(display="inline-block") == [
        "placeholder",
        "d-inline-block",
    ]
    assert placeholder_structural_classes(size="lg", lg=6) == [
        "placeholder",
        "placeholder-lg",
        "col-lg-6",
    ]


def test_placeholder_validation() -> None:
    with pytest.raises(ValueError, match="Unknown placeholder animation"):
        placeholder_structural_classes(animation="spin")
    with pytest.raises(ValueError, match="Unknown placeholder animation"):
        Placeholder(animation="spin")
    with pytest.raises(ValueError, match="Unknown placeholder size"):
        placeholder_structural_classes(size="md")
    with pytest.raises(ValueError, match="Unknown placeholder size"):
        Placeholder(size="md")
    with pytest.raises(ValueError, match="Unknown column width"):
        placeholder_structural_classes(xs=13)
    with pytest.raises(ValueError, match="Unknown column width"):
        placeholder_structural_classes(md=0)
    with pytest.raises(ValueError, match="Unknown placeholder width"):
        placeholder_structural_classes(width=20)
    with pytest.raises(ValueError, match="Unknown placeholder width"):
        Placeholder(width=True)
    with pytest.raises(ValueError, match="Unknown display"):
        placeholder_structural_classes(display="banana")
    with pytest.raises(ValueError, match="Unknown display"):
        Placeholder(display="banana")


@pytest.mark.parametrize(
    ("helper", "kwargs"),
    [
        (card_structural_classes, {"color": "nope"}),
        (list_group_item_structural_classes, {"color": "nope"}),
        (table_structural_classes, {"color": "nope"}),
        (badge_structural_classes, {"color": "nope"}),
        (progress_bar_structural_classes, {"color": "nope"}),
        (placeholder_structural_classes, {"color": "nope"}),
    ],
)
def test_unknown_color_rejected(helper: Callable[..., list[str]], kwargs: dict[str, str]) -> None:
    with pytest.raises(ValueError, match="Unknown color"):
        helper(**kwargs)


def test_unknown_color_rejected_before_construction() -> None:
    with pytest.raises(ValueError, match="Unknown color"):
        Card(color="nope")
    with pytest.raises(ValueError, match="Unknown color"):
        ListGroupItem(color="nope")
    with pytest.raises(ValueError, match="Unknown color"):
        Table(color="nope")
    with pytest.raises(ValueError, match="Unknown color"):
        Badge(color="nope")
    with pytest.raises(ValueError, match="Unknown color"):
        Progress(color="nope")
    with pytest.raises(ValueError, match="Unknown color"):
        Placeholder(color="nope")


@pytest.mark.user
async def test_content_components_render(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        Card("Card text")
        Badge("New")

    await user.open("/")
    await user.should_see("Card text")
    await user.should_see("New")


@pytest.mark.user
async def test_table_from_dataframe(user: User) -> None:
    pd = pytest.importorskip("pandas")
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        frame = pd.DataFrame({"a": [1], "b": [2]})
        Table.from_dataframe(frame, index=False)

    await user.open("/")
    await user.should_see("a")
    await user.should_see("1")
