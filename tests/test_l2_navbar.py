"""L2 tests for the navbar family."""

from __future__ import annotations

from typing import Any

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components._base import (
    ChildrenError,
    PropConflictError,
    UnsupportedPropError,
)
from nicegui_bootstrap_components.bs._navbar import (
    DbcNavbar,
    DbcNavbarBrand,
    DbcNavbarSimple,
    DbcNavbarToggler,
    Navbar,
    NavbarBrand,
    NavbarSimple,
    NavbarToggler,
    navbar,
    navbar_brand,
    navbar_color_class,
    navbar_expand_class,
    navbar_position_classes,
    navbar_simple,
    navbar_structural_classes,
    navbar_theme_value,
    navbar_toggler,
)

pytest_plugins = ["nicegui.testing.plugin"]


def _slot_children(el: Any) -> list[Any]:
    slot = getattr(el, "default_slot", None)
    if slot is None:
        slots = getattr(el, "slots", None)
        if isinstance(slots, dict):
            slot = slots.get("default")
    if slot is None:
        return []
    return list(getattr(slot, "children", []))


def _navbar_simple_parts(simple: Any) -> tuple[Any, Any]:
    inner = _slot_children(_slot_children(simple)[0])
    return inner[-2], inner[-1]


class _OpenTarget:
    def __init__(self) -> None:
        self.is_open = False


def test_surface_identities() -> None:
    assert Navbar is not DbcNavbar
    assert navbar is Navbar
    assert Navbar.component_name == "Navbar"
    assert DbcNavbar.component_name == "Navbar"

    assert NavbarBrand is not DbcNavbarBrand
    assert navbar_brand is NavbarBrand
    assert NavbarBrand.component_name == "NavbarBrand"
    assert DbcNavbarBrand.component_name == "NavbarBrand"

    assert NavbarToggler is not DbcNavbarToggler
    assert navbar_toggler is NavbarToggler
    assert NavbarToggler.component_name == "NavbarToggler"
    assert DbcNavbarToggler.component_name == "NavbarToggler"

    assert NavbarSimple is not DbcNavbarSimple
    assert navbar_simple is NavbarSimple
    assert NavbarSimple.component_name == "NavbarSimple"
    assert DbcNavbarSimple.component_name == "NavbarSimple"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        (False, None),
        (True, "navbar-expand"),
        ("sm", "navbar-expand-sm"),
        ("md", "navbar-expand-md"),
        ("lg", "navbar-expand-lg"),
        ("xl", "navbar-expand-xl"),
        ("xxl", "navbar-expand-xxl"),
    ],
)
def test_navbar_expand_class(value: bool | str | None, expected: str | None) -> None:
    assert navbar_expand_class(value) == expected


@pytest.mark.parametrize("value", ["", "xs", "MD", "foo", "true"])
def test_navbar_expand_class_invalid(value: str) -> None:
    with pytest.raises(ValueError, match="expand"):
        navbar_expand_class(value)


@pytest.mark.parametrize(
    "color",
    [
        "primary",
        "secondary",
        "success",
        "danger",
        "warning",
        "info",
        "light",
        "dark",
        "white",
        "transparent",
        "body-secondary",
        "custom",
    ],
)
def test_navbar_color_class(color: str) -> None:
    assert navbar_color_class(color) == f"bg-{color}"


def test_navbar_color_class_none() -> None:
    assert navbar_color_class(None) is None


@pytest.mark.parametrize("color", ["", "#fff", "rgb(0,0,0)", "1red", " primary"])
def test_navbar_color_class_invalid(color: str) -> None:
    with pytest.raises(ValueError, match="color"):
        navbar_color_class(color)


def test_navbar_position_classes() -> None:
    assert navbar_position_classes() == []
    assert navbar_position_classes(fixed="top") == ["fixed-top"]
    assert navbar_position_classes(fixed="bottom") == ["fixed-bottom"]
    assert navbar_position_classes(sticky="top") == ["sticky-top"]


def test_navbar_position_classes_conflict() -> None:
    with pytest.raises(PropConflictError, match="fixed"):
        navbar_position_classes(fixed="top", sticky="top")


def test_navbar_position_classes_invalid_fixed() -> None:
    with pytest.raises(ValueError, match="fixed"):
        navbar_position_classes(fixed="left")


def test_navbar_position_classes_invalid_sticky() -> None:
    with pytest.raises(ValueError, match="sticky"):
        navbar_position_classes(sticky="bottom")


def test_navbar_theme_value() -> None:
    assert navbar_theme_value(True) == "dark"
    assert navbar_theme_value(False) is None
    assert navbar_theme_value(None) is None


def test_navbar_structural_classes_mapping() -> None:
    assert navbar_structural_classes() == ["navbar"]
    assert navbar_structural_classes(expand=False) == ["navbar"]
    assert navbar_structural_classes(expand=True) == ["navbar", "navbar-expand"]
    assert navbar_structural_classes(expand="md") == ["navbar", "navbar-expand-md"]
    assert navbar_structural_classes(color="primary") == ["navbar", "bg-primary"]
    assert navbar_structural_classes(fixed="top") == ["navbar", "fixed-top"]
    assert navbar_structural_classes(fixed="bottom") == ["navbar", "fixed-bottom"]
    assert navbar_structural_classes(sticky="top") == ["navbar", "sticky-top"]
    assert navbar_structural_classes(color="dark", expand=True, fixed="top") == [
        "navbar",
        "navbar-expand",
        "bg-dark",
        "fixed-top",
    ]
    assert navbar_structural_classes(color="info", sticky="top") == [
        "navbar",
        "bg-info",
        "sticky-top",
    ]


def test_navbar_structural_classes_conflict() -> None:
    with pytest.raises(PropConflictError, match="sticky"):
        navbar_structural_classes(fixed="bottom", sticky="top")


def test_navbar_invalid_expand_raises_before_construction() -> None:
    with pytest.raises(ValueError, match="expand"):
        Navbar(expand="nope")


def test_navbar_invalid_fixed_raises_before_construction() -> None:
    with pytest.raises(ValueError, match="fixed"):
        Navbar(fixed="middle")


def test_navbar_invalid_sticky_raises_before_construction() -> None:
    with pytest.raises(ValueError, match="sticky"):
        Navbar(sticky="bottom")


def test_navbar_fixed_sticky_conflict_raises_before_construction() -> None:
    with pytest.raises(PropConflictError, match="fixed"):
        Navbar(fixed="top", sticky="top")


def test_navbar_invalid_color_raises_before_construction() -> None:
    with pytest.raises(ValueError, match="color"):
        Navbar(color="#fff")


def test_dbc_navbar_rejects_light() -> None:
    with pytest.raises(UnsupportedPropError, match="light"):
        DbcNavbar(light=True)


def test_dbc_navbar_simple_rejects_light() -> None:
    with pytest.raises(UnsupportedPropError, match="light"):
        DbcNavbarSimple(light=False)


def test_navbar_simple_rejects_text_children() -> None:
    with pytest.raises(ChildrenError, match="wrap text"):
        NavbarSimple(children="hello")


def test_navbar_simple_rejects_text_in_child_list() -> None:
    with pytest.raises(ChildrenError, match="wrap text"):
        NavbarSimple(children=["hello"])


def test_navbar_simple_invalid_expand_raises_before_construction() -> None:
    with pytest.raises(ValueError, match="expand"):
        NavbarSimple(expand="xs")


def test_navbar_simple_fixed_sticky_conflict_raises_before_construction() -> None:
    with pytest.raises(PropConflictError, match="fixed"):
        NavbarSimple(fixed="top", sticky="top")


@pytest.mark.user
async def test_navbar_renders(user: User) -> None:
    seen: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        seen["navbar"] = Navbar(
            color="primary",
            dark=True,
            expand="lg",
            fixed="top",
        )
        seen["sticky"] = Navbar(sticky="top", expand=False)

    await user.open("/")
    el = seen["navbar"]
    assert el.tag == "nav"
    assert "navbar" in el._classes
    assert "bg-primary" in el._classes
    assert "navbar-expand-lg" in el._classes
    assert "fixed-top" in el._classes
    assert el._props.get("data-bs-theme") == "dark"

    sticky = seen["sticky"]
    assert sticky.tag == "nav"
    assert "navbar" in sticky._classes
    assert "sticky-top" in sticky._classes
    assert "navbar-expand" not in sticky._classes
    assert "data-bs-theme" not in sticky._props


@pytest.mark.user
async def test_brand_and_toggler_markup(user: User) -> None:
    seen: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        seen["with_href"] = NavbarBrand("Site", href="https://example.com", external_link=True)
        seen["no_href"] = NavbarBrand("Site")
        seen["toggler"] = NavbarToggler()

    await user.open("/")
    await user.should_see("Site")

    with_href = seen["with_href"]
    assert with_href.tag == "a"
    assert "navbar-brand" in with_href._classes
    assert with_href._props.get("href") == "https://example.com"
    assert with_href._props.get("target") == "_blank"
    assert with_href._props.get("rel") == "noopener noreferrer"

    no_href = seen["no_href"]
    assert no_href.tag == "span"
    assert "navbar-brand" in no_href._classes
    assert "href" not in no_href._props

    tog = seen["toggler"]
    assert tog.tag == "button"
    assert "navbar-toggler" in tog._classes
    assert tog._props.get("type") == "button"
    assert "data-bs-toggle" not in tog._props
    icons = [c for c in _slot_children(tog) if "navbar-toggler-icon" in c._classes]
    assert len(icons) == 1
    assert icons[0].tag == "span"


@pytest.mark.user
async def test_navbar_simple_composition(user: User) -> None:
    seen: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        seen["simple"] = NavbarSimple(
            brand="App",
            brand_href="/",
            color="dark",
            dark=True,
            expand="md",
            fluid=True,
            links_left=True,
            fixed="top",
        )

    await user.open("/")
    await user.should_see("App")

    simple = seen["simple"]
    assert simple.tag == "nav"
    assert "navbar" in simple._classes
    assert "navbar-expand-md" in simple._classes
    assert "bg-dark" in simple._classes
    assert "fixed-top" in simple._classes
    assert simple._props.get("data-bs-theme") == "dark"

    container = _slot_children(simple)[0]
    assert "container-fluid" in container._classes

    inner = _slot_children(container)
    assert len(inner) == 3
    brand, tog, collapse = inner
    assert "navbar-brand" in brand._classes
    assert brand.tag == "a"
    assert brand._props.get("href") == "/"
    assert "navbar-toggler" in tog._classes
    assert tog.tag == "button"
    assert "collapse" in collapse._classes
    assert "navbar-collapse" in collapse._classes

    nav_wrap = _slot_children(collapse)[0]
    assert "navbar-nav" in nav_wrap._classes
    assert "me-auto" in nav_wrap._classes


@pytest.mark.user
async def test_expand_fixed_sticky_theme_both_surfaces(user: User) -> None:
    seen: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        for bp in ("sm", "md", "lg", "xl", "xxl"):
            seen[f"nav-{bp}"] = Navbar(expand=bp)
            seen[f"dbc-{bp}"] = DbcNavbar(expand=bp)
            seen[f"simple-{bp}"] = NavbarSimple(expand=bp)
            seen[f"dsimple-{bp}"] = DbcNavbarSimple(expand=bp)
        seen["nav-true"] = Navbar(expand=True)
        seen["nav-false"] = Navbar(expand=False)
        seen["simple-true"] = NavbarSimple(expand=True)
        seen["simple-false"] = NavbarSimple(expand=False)
        seen["fixed-top"] = Navbar(fixed="top")
        seen["fixed-bottom"] = Navbar(fixed="bottom")
        seen["sticky-top"] = Navbar(sticky="top")
        seen["dbc-fixed"] = DbcNavbar(fixed="bottom")
        seen["dbc-sticky"] = DbcNavbar(sticky="top")
        seen["simple-fixed"] = NavbarSimple(fixed="top")
        seen["simple-sticky"] = NavbarSimple(sticky="top")
        seen["dsimple-fixed"] = DbcNavbarSimple(fixed="bottom")
        seen["nav-dark"] = Navbar(dark=True)
        seen["nav-nodark"] = Navbar(dark=False)
        seen["dbc-dark"] = DbcNavbar(dark=True)
        seen["simple-dark"] = NavbarSimple(dark=True)
        seen["dsimple-dark"] = DbcNavbarSimple(dark=True)
        seen["simple-nodark"] = NavbarSimple(dark=None)

    await user.open("/")

    for bp in ("sm", "md", "lg", "xl", "xxl"):
        cls = f"navbar-expand-{bp}"
        assert cls in seen[f"nav-{bp}"]._classes
        assert cls in seen[f"dbc-{bp}"]._classes
        assert cls in seen[f"simple-{bp}"]._classes
        assert cls in seen[f"dsimple-{bp}"]._classes

    assert "navbar-expand" in seen["nav-true"]._classes
    assert "navbar-expand" not in seen["nav-false"]._classes
    assert "navbar-expand" in seen["simple-true"]._classes
    assert "navbar-expand" not in seen["simple-false"]._classes

    assert "fixed-top" in seen["fixed-top"]._classes
    assert "fixed-bottom" in seen["fixed-bottom"]._classes
    assert "sticky-top" in seen["sticky-top"]._classes
    assert "fixed-bottom" in seen["dbc-fixed"]._classes
    assert "sticky-top" in seen["dbc-sticky"]._classes
    assert "fixed-top" in seen["simple-fixed"]._classes
    assert "sticky-top" in seen["simple-sticky"]._classes
    assert "fixed-bottom" in seen["dsimple-fixed"]._classes

    assert seen["nav-dark"]._props.get("data-bs-theme") == "dark"
    assert "data-bs-theme" not in seen["nav-nodark"]._props
    assert seen["dbc-dark"]._props.get("data-bs-theme") == "dark"
    assert seen["simple-dark"]._props.get("data-bs-theme") == "dark"
    assert seen["dsimple-dark"]._props.get("data-bs-theme") == "dark"
    assert "data-bs-theme" not in seen["simple-nodark"]._props


@pytest.mark.user
async def test_navbar_simple_is_open_parity(user: User) -> None:
    seen: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        seen["native"] = NavbarSimple(brand="Native")
        seen["open"] = NavbarSimple(brand="Opened", is_open=True)
        seen["dbc"] = DbcNavbarSimple(brand="Compat")
        seen["dbc-open"] = DbcNavbarSimple(brand="CompatOpen", is_open=True)

    await user.open("/")

    native = seen["native"]
    tog, collapse = _navbar_simple_parts(native)
    assert native.is_open is False
    assert "show" not in collapse._classes

    native.is_open = True
    assert native.is_open is True
    assert "show" in collapse._classes

    tog._handle_click()
    assert native.is_open is False
    assert "show" not in collapse._classes
    assert tog.n_clicks == 1

    tog._handle_click()
    assert native.is_open is True
    assert "show" in collapse._classes
    assert tog.n_clicks == 2

    opened = seen["open"]
    _, open_collapse = _navbar_simple_parts(opened)
    assert opened.is_open is True
    assert "show" in open_collapse._classes

    dbc = seen["dbc"]
    dbc_tog, dbc_collapse = _navbar_simple_parts(dbc)
    assert dbc.is_open is False
    dbc_tog._handle_click()
    assert dbc.is_open is True
    assert "show" in dbc_collapse._classes
    dbc.is_open = False
    assert dbc.is_open is False
    assert "show" not in dbc_collapse._classes

    dbc_open = seen["dbc-open"]
    _, dbc_open_collapse = _navbar_simple_parts(dbc_open)
    assert dbc_open.is_open is True
    assert "show" in dbc_open_collapse._classes


@pytest.mark.user
async def test_navbar_toggler_target_forms(user: User) -> None:
    seen: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        obj = _OpenTarget()
        other = _OpenTarget()
        seen["obj"] = obj
        seen["other"] = other
        seen["none"] = NavbarToggler()
        seen["elem"] = NavbarToggler(target=obj, n_clicks=3)
        seen["missing"] = NavbarToggler(target="navbar-toggler-missing")
        host = Navbar(id="navbar-toggler-host")
        seen["host"] = host
        seen["by-id"] = NavbarToggler(target="navbar-toggler-host")
        seen["dbc"] = DbcNavbarToggler(target=other, n_clicks=1)

    await user.open("/")

    none = seen["none"]
    assert none.target is None
    assert none.n_clicks == 0
    none._handle_click()
    assert none.n_clicks == 1

    elem = seen["elem"]
    assert elem.target is seen["obj"]
    assert elem.n_clicks == 3
    assert seen["obj"].is_open is False
    elem._handle_click()
    assert elem.n_clicks == 4
    assert seen["obj"].is_open is True
    elem._handle_click()
    assert seen["obj"].is_open is False

    missing = seen["missing"]
    assert missing.target == "navbar-toggler-missing"
    missing._handle_click()
    assert missing.n_clicks == 1

    by_id = seen["by-id"]
    assert by_id.target == "navbar-toggler-host"
    by_id._handle_click()
    assert by_id.n_clicks == 1

    dbc = seen["dbc"]
    assert dbc.n_clicks == 1
    dbc._handle_click()
    assert dbc.n_clicks == 2
    assert seen["other"].is_open is True


@pytest.mark.user
async def test_navbar_forwards_children_and_simple_extras(user: User) -> None:
    seen: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        brand = NavbarBrand("Forward")
        toggler = NavbarToggler()
        seen["brand"] = brand
        seen["toggler"] = toggler
        seen["nav"] = Navbar(children=[brand, toggler], color="light")
        seen["dbc-nav"] = DbcNavbar(children=[NavbarBrand("CompatChild")])
        seen["simple"] = NavbarSimple(
            brand="Extras",
            brand_href="https://example.com",
            brand_external_link=True,
            brand_style={"color": "red"},
            expand=True,
            fluid=False,
            links_left=False,
        )

    await user.open("/")
    await user.should_see("Forward")

    kids = _slot_children(seen["nav"])
    assert kids == [seen["brand"], seen["toggler"]]
    assert seen["nav"].tag == "nav"
    assert "navbar" in seen["nav"]._classes
    assert "bg-light" in seen["nav"]._classes

    dbc_kids = _slot_children(seen["dbc-nav"])
    assert len(dbc_kids) == 1
    assert "navbar-brand" in dbc_kids[0]._classes

    simple = seen["simple"]
    assert "navbar-expand" in simple._classes
    container = _slot_children(simple)[0]
    assert "container" in container._classes
    assert "container-fluid" not in container._classes
    inner = _slot_children(container)
    assert len(inner) == 3
    brand, tog, collapse = inner
    assert brand.tag == "a"
    assert brand._props.get("href") == "https://example.com"
    assert brand._props.get("target") == "_blank"
    assert brand._props.get("rel") == "noopener noreferrer"
    assert "navbar-toggler" in tog._classes
    assert "collapse" in collapse._classes
    assert "navbar-collapse" in collapse._classes
    assert "show" not in collapse._classes
    nav_wrap = _slot_children(collapse)[0]
    assert "navbar-nav" in nav_wrap._classes
    assert "ms-auto" in nav_wrap._classes
    assert simple.is_open is False
