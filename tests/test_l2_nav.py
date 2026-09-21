"""L1 tests for the navigation family."""

from __future__ import annotations

from contextlib import suppress

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components._base import ChildrenError
from nicegui_bootstrap_components.bs._nav import (
    Breadcrumb,
    DbcBreadcrumb,
    DbcNav,
    DbcNavItem,
    DbcNavLink,
    DbcPagination,
    Nav,
    NavItem,
    NavLink,
    Pagination,
    breadcrumb,
    breadcrumb_item_classes,
    clamp_page,
    nav,
    nav_classes,
    nav_item,
    nav_link,
    nav_link_classes,
    pagination,
    pagination_tokens,
    validate_breadcrumb_items,
)

pytest_plugins = ["nicegui.testing.plugin"]
pytestmark = pytest.mark.user


def test_nav_classes() -> None:
    assert nav_classes() == ["nav"]
    assert nav_classes(pills=True) == ["nav", "nav-pills"]
    assert nav_classes(navbar=True) == ["navbar-nav"]
    assert nav_classes(navbar=True, navbar_scroll=True) == ["navbar-nav", "navbar-nav-scroll"]
    assert nav_classes(fill=True) == ["nav", "nav-fill"]
    assert nav_classes(justified=True) == ["nav", "nav-justified"]
    assert nav_classes(vertical=True) == ["nav", "flex-column"]
    assert nav_classes(vertical="sm") == ["nav", "flex-sm-column"]
    with pytest.raises(ValueError):
        nav_classes(vertical="xxl")
    assert nav_classes(horizontal="start") == ["nav", "justify-content-start"]
    with pytest.raises(ValueError):
        nav_classes(horizontal="nope")
    assert nav_classes(horizontal="between") == ["nav", "justify-content-between"]
    assert "card-header-pills" in nav_classes(card=True, pills=True)
    assert nav_classes(card=True) == ["nav"]
    assert "card-header-pills" not in nav_classes(card=True)


def test_nav_link_classes() -> None:
    assert nav_link_classes() == ["nav-link"]
    assert nav_link_classes(active=True) == ["nav-link", "active"]
    assert nav_link_classes(active="exact") == ["nav-link", "active"]
    assert nav_link_classes(disabled=True) == ["nav-link", "disabled"]
    assert nav_link_classes(active=True, disabled=True) == ["nav-link", "active", "disabled"]


def test_breadcrumb_item_classes() -> None:
    assert breadcrumb_item_classes() == ["breadcrumb-item"]
    assert breadcrumb_item_classes(active=True) == ["breadcrumb-item", "active"]


def test_validate_breadcrumb_items() -> None:
    payload = {"label": "Home", "href": "/"}
    snapshot = dict(payload)
    validated = validate_breadcrumb_items([payload])
    assert validated == [payload]
    assert validated[0] is not payload
    assert payload == snapshot
    with pytest.raises(ValueError):
        validate_breadcrumb_items([{"href": "/"}])
    with pytest.raises(ValueError):
        validate_breadcrumb_items([{"label": ""}])
    with pytest.raises(TypeError):
        validate_breadcrumb_items(["Home"])
    with suppress(Exception):
        Breadcrumb(items=[payload])
    assert payload == snapshot


def test_pagination_tokens() -> None:
    assert pagination_tokens(min_value=1, max_value=5, step=1, active_page=1) == [1, 2, 3, 4, 5]
    assert pagination_tokens(
        min_value=1,
        max_value=5,
        step=1,
        active_page=1,
        previous_next=True,
        first_last=True,
    ) == ["first", "prev", 1, 2, 3, 4, 5, "next", "last"]
    assert pagination_tokens(
        min_value=1,
        max_value=100,
        step=1,
        active_page=2,
        fully_expanded=False,
    ) == [1, 2, 3, 4, 5, "ellipsis", 100]
    assert pagination_tokens(
        min_value=1,
        max_value=100,
        step=1,
        active_page=50,
        fully_expanded=False,
    ) == [1, "ellipsis", 49, 50, 51, "ellipsis", 100]
    assert pagination_tokens(
        min_value=1,
        max_value=100,
        step=1,
        active_page=99,
        fully_expanded=False,
    ) == [1, "ellipsis", 96, 97, 98, 99, 100]
    assert pagination_tokens(
        min_value=1, max_value=9, step=3, active_page=1, fully_expanded=True
    ) == [1, 4, 7, 10]
    assert pagination_tokens(min_value=1, max_value=10, step=3, active_page=1) == [1, 4, 7, 10]
    assert pagination_tokens(
        min_value=1, max_value=7, step=1, active_page=1, fully_expanded=False
    ) == [1, 2, 3, 4, 5, 6, 7]


def test_clamp_page() -> None:
    assert clamp_page(0, min_value=1, max_value=5) == 1
    assert clamp_page(999, min_value=1, max_value=5) == 5
    assert clamp_page(3, min_value=1, max_value=5) == 3


def test_pagination_rejects_children() -> None:
    with pytest.raises(
        ChildrenError, match="Pagination generates its own items; do not pass children"
    ):
        Pagination(children=["x"], max_value=5)


def test_pagination_validates_params() -> None:
    with pytest.raises(ValueError):
        Pagination(max_value=1, min_value=5)
    with pytest.raises(ValueError):
        Pagination(max_value=5, step=0)
    with pytest.raises(ValueError):
        Pagination(max_value=5, size="xl")


def test_surface_identities() -> None:
    assert Nav is not DbcNav
    assert nav is Nav
    assert Nav.component_name == "Nav"
    assert DbcNav.component_name == "Nav"
    assert NavItem is not DbcNavItem
    assert nav_item is NavItem
    assert NavItem.component_name == "NavItem"
    assert DbcNavItem.component_name == "NavItem"
    assert NavLink is not DbcNavLink
    assert nav_link is NavLink
    assert NavLink.component_name == "NavLink"
    assert DbcNavLink.component_name == "NavLink"
    assert Breadcrumb is not DbcBreadcrumb
    assert breadcrumb is Breadcrumb
    assert Breadcrumb.component_name == "Breadcrumb"
    assert DbcBreadcrumb.component_name == "Breadcrumb"
    assert Pagination is not DbcPagination
    assert pagination is Pagination
    assert Pagination.component_name == "Pagination"
    assert DbcPagination.component_name == "Pagination"


async def test_nav_renders_nav_links(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with Nav():
            NavLink("Home")
            NavLink("About")

    await user.open("/")
    await user.should_see("Home")
    await user.should_see("About")


async def test_breadcrumb_renders_items(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        Breadcrumb(
            items=[
                {"label": "Home", "href": "/"},
                {"label": "Library", "active": True},
            ]
        )

    await user.open("/")
    await user.should_see("Home")
    await user.should_see("Library")


async def test_pagination_renders_pages(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        Pagination(max_value=5)

    await user.open("/")
    await user.should_see("3")
    await user.should_see("5")
