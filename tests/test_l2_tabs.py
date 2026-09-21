"""L2 tests for the tabs family."""

from __future__ import annotations

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components._base import ChildrenError, UnsupportedPropError
from nicegui_bootstrap_components.bs._tabs import (
    DbcTab,
    DbcTabs,
    Tab,
    Tabs,
    assign_tab_ids,
    first_enabled_tab_id,
    tab,
    tab_button_aria,
    tab_link_classes,
    tab_pane_aria,
    tab_pane_classes,
    tabs,
    tabs_card_body_classes,
    tabs_card_header_classes,
    tabs_content_classes,
    tabs_nav_classes,
    tabs_nav_item_classes,
    tabs_structural_classes,
)

pytest_plugins = ["nicegui.testing.plugin"]
pytestmark = pytest.mark.user


def test_tabs_identity_pairs() -> None:
    assert Tabs is not DbcTabs
    assert tabs is Tabs
    assert Tabs.component_name == "Tabs"
    assert Tab is not DbcTab
    assert tab is Tab
    assert Tab.component_name == "Tab"
    assert Tab.reserved_classes == ("tab-pane",)


def test_assign_tab_ids_stable_index_order() -> None:
    assert assign_tab_ids([]) == []
    assert assign_tab_ids([None, None, None]) == ["tab-0", "tab-1", "tab-2"]
    assert assign_tab_ids(["home", None, None]) == ["home", "tab-1", "tab-2"]
    assert assign_tab_ids(["tab-0", "custom", None]) == ["tab-0", "custom", "tab-2"]


def test_assign_tab_ids_preserves_explicit_and_avoids_collisions() -> None:
    assert assign_tab_ids(["home", None, "profile"]) == ["home", "tab-1", "profile"]
    assert assign_tab_ids([None, "tab-0"]) == ["tab-1", "tab-0"]
    assert assign_tab_ids([None, "tab-0", None]) == ["tab-1", "tab-0", "tab-2"]


def test_first_enabled_tab_id() -> None:
    assert first_enabled_tab_id([], []) is None
    assert first_enabled_tab_id(["a", "b"], [False, False]) == "a"
    assert first_enabled_tab_id(["a", "b"], [True, False]) == "b"
    assert first_enabled_tab_id(["a"], [True]) is None


def test_tabs_class_helpers() -> None:
    assert tabs_structural_classes() == []
    assert tabs_structural_classes(card=True) == ["card"]
    assert tabs_nav_classes() == ["nav", "nav-tabs"]
    assert tabs_nav_classes(card=True) == ["nav", "nav-tabs", "card-header-tabs"]
    assert tabs_nav_item_classes() == ["nav-item"]
    assert tabs_card_header_classes() == ["card-header"]
    assert tabs_card_body_classes() == ["card-body"]
    assert tabs_content_classes() == ["tab-content"]
    assert tab_link_classes() == ["nav-link"]
    assert tab_link_classes(active=True) == ["nav-link", "active"]
    assert tab_link_classes(disabled=True) == ["nav-link", "disabled"]
    assert tab_link_classes(active=True, disabled=True) == ["nav-link", "active", "disabled"]
    assert tab_pane_classes() == ["tab-pane"]
    assert tab_pane_classes(active=True) == ["tab-pane", "active"]


def test_tab_aria_helpers() -> None:
    assert tab_button_aria(tab_id="home", pane_id="home", selected=True) == {
        "role": "tab",
        "id": "home-tab",
        "aria-controls": "home",
        "aria-selected": "true",
        "tabindex": "0",
    }
    disabled = tab_button_aria(tab_id="x", pane_id="x", selected=False, disabled=True)
    assert disabled["aria-disabled"] == "true"
    assert disabled["tabindex"] == "-1"
    assert disabled["aria-selected"] == "false"
    assert tab_pane_aria(tab_id="home", pane_id="home", selected=True) == {
        "role": "tabpanel",
        "id": "home",
        "aria-labelledby": "home-tab",
        "aria-hidden": "false",
    }
    assert tab_pane_aria(tab_id="home", pane_id="home", selected=False)["aria-hidden"] == "true"


def test_tabs_rejects_text_children() -> None:
    with pytest.raises(ChildrenError, match="wrap text"):
        Tabs("hello")
    with pytest.raises(ChildrenError, match="wrap text"):
        Tabs(["hello"])


def test_tabs_rejects_non_tab_children() -> None:
    with pytest.raises(ChildrenError, match="Tab"):
        Tabs([object()])


def test_compat_rejects_native_only_props() -> None:
    with pytest.raises(UnsupportedPropError, match="lazy"):
        DbcTabs(lazy=True)
    with pytest.raises(UnsupportedPropError, match="on_change"):
        DbcTabs(on_change=lambda tab_id: None)
    with pytest.raises(UnsupportedPropError, match="persist"):
        DbcTabs(persist="local")


def test_invalid_persist_value() -> None:
    with pytest.raises(ValueError, match="persist"):
        Tabs(persist="cookie")


async def test_tabs_ids_default_aria_and_disabled(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    holder: list[Tabs] = []

    @ui.page("/")
    def page() -> None:
        holder.append(
            Tabs(
                [
                    Tab("Off pane", label="Off", tab_id="off", disabled=True),
                    Tab("On pane", label="On", tab_id="on"),
                    Tab("Third pane", label="Third"),
                ]
            )
        )

    await user.open("/")
    widget = holder[0]
    assert widget.tab_ids == ["off", "on", "tab-2"]
    assert widget.active_tab == "on"
    assert widget._nav._props.get("role") == "tablist"
    button = widget._buttons["on"]
    assert button._props.get("role") == "tab"
    assert button._props.get("aria-selected") == "true"
    assert button._props.get("aria-controls") == "on"
    assert button._props.get("id") == "on-tab"
    off_button = widget._buttons["off"]
    assert off_button._props.get("aria-disabled") == "true"
    widget._on_tab_click("off")
    assert widget.active_tab == "on"
    widget.active_tab = "tab-2"
    assert widget.active_tab == "tab-2"
    await user.should_see("On")
    await user.should_see("Third")


async def test_tabs_card_classes_and_change(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    holder: list[Tabs] = []
    seen: list[str] = []

    @ui.page("/")
    def page() -> None:
        holder.append(
            Tabs(
                [
                    Tab(label="Home", tab_id="home"),
                    Tab(label="Profile", tab_id="profile"),
                ],
                card=True,
                on_change=seen.append,
            )
        )

    await user.open("/")
    widget = holder[0]
    assert "card" in widget.classes
    assert "card-header-tabs" in widget._nav.classes
    assert widget._header is not None
    assert "card-header" in widget._header.classes
    assert widget._body is not None
    assert "card-body" in widget._body.classes
    assert "tab-content" in widget._content.classes
    assert widget.active_tab == "home"
    widget._on_tab_click("profile")
    assert widget.active_tab == "profile"
    assert seen == ["profile"]
    await user.should_see("Home")
    await user.should_see("Profile")


async def test_tabs_dynamic_insert_remove(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    holder: list[Tabs] = []

    @ui.page("/")
    def page() -> None:
        first = Tab(label="A")
        second = Tab(label="B", tab_id="keep")
        widget = Tabs([first, second])
        with widget:
            Tab(label="C")
        second.delete()
        holder.append(widget)

    await user.open("/")
    widget = holder[0]
    assert widget.tab_ids == ["tab-0", "tab-2"]
    assert widget.active_tab == "tab-0"
    await user.should_see("A")
    await user.should_see("C")
