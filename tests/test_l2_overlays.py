"""L2 tests for overlay and disclosure components."""

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components._base import PropConflictError, UnsupportedPropError
from nicegui_bootstrap_components.bs._overlays import (
    Accordion,
    AccordionItem,
    Collapse,
    DbcAccordion,
    DbcAccordionItem,
    DbcCollapse,
    DbcDropdownMenu,
    DbcDropdownMenuItem,
    DbcFade,
    DbcModal,
    DbcModalBody,
    DbcModalFooter,
    DbcModalHeader,
    DbcModalTitle,
    DbcOffcanvas,
    DbcTooltip,
    DropdownMenu,
    DropdownMenuItem,
    Fade,
    Modal,
    ModalBody,
    ModalFooter,
    ModalHeader,
    ModalTitle,
    Offcanvas,
    Tooltip,
    accordion,
    accordion_item,
    accordion_structural_classes,
    collapse,
    collapse_structural_classes,
    dropdown_direction_class,
    dropdown_item_inner_classes,
    dropdown_menu,
    dropdown_menu_classes,
    dropdown_menu_item,
    dropdown_root_classes,
    dropdown_toggle_classes,
    fade,
    fade_structural_classes,
    generate_accordion_item_ids,
    modal,
    modal_body,
    modal_dialog_classes,
    modal_footer,
    modal_header,
    modal_title,
    offcanvas,
    offcanvas_structural_classes,
    resolve_accordion_active,
    tooltip,
)

pytest_plugins = ["nicegui.testing.plugin"]


@pytest.mark.parametrize(
    ("native", "compat", "alias", "name"),
    [
        (Modal, DbcModal, modal, "Modal"),
        (ModalHeader, DbcModalHeader, modal_header, "ModalHeader"),
        (ModalTitle, DbcModalTitle, modal_title, "ModalTitle"),
        (ModalBody, DbcModalBody, modal_body, "ModalBody"),
        (ModalFooter, DbcModalFooter, modal_footer, "ModalFooter"),
        (Collapse, DbcCollapse, collapse, "Collapse"),
        (Fade, DbcFade, fade, "Fade"),
        (Offcanvas, DbcOffcanvas, offcanvas, "Offcanvas"),
        (DropdownMenu, DbcDropdownMenu, dropdown_menu, "DropdownMenu"),
        (DropdownMenuItem, DbcDropdownMenuItem, dropdown_menu_item, "DropdownMenuItem"),
        (Accordion, DbcAccordion, accordion, "Accordion"),
        (AccordionItem, DbcAccordionItem, accordion_item, "AccordionItem"),
        (Tooltip, DbcTooltip, tooltip, "Tooltip"),
    ],
)
def test_surface_identity(native: type, compat: type, alias: object, name: str) -> None:
    assert native is not compat
    assert alias is native
    assert native.component_name == name


def test_dropdown_direction_class() -> None:
    assert dropdown_direction_class("down") == "dropdown"
    assert dropdown_direction_class("up") == "dropup"
    assert dropdown_direction_class("start") == "dropstart"
    assert dropdown_direction_class("end") == "dropend"
    assert dropdown_direction_class("left") == "dropstart"
    assert dropdown_direction_class("right") == "dropend"
    with pytest.raises(ValueError, match="direction"):
        dropdown_direction_class("sideways")


def test_dropdown_root_classes() -> None:
    assert dropdown_root_classes() == ["dropdown"]
    assert dropdown_root_classes(direction="up") == ["dropup"]
    assert dropdown_root_classes(group=True) == ["btn-group"]
    assert dropdown_root_classes(group=True, direction="up") == ["btn-group", "dropup"]
    assert dropdown_root_classes(nav=True) == ["dropdown", "nav-item"]
    assert dropdown_root_classes(in_navbar=True) == ["dropdown", "nav-item"]
    with pytest.raises(ValueError, match="direction"):
        dropdown_root_classes(direction="sideways")


def test_dropdown_toggle_classes() -> None:
    assert dropdown_toggle_classes() == ["btn", "btn-secondary", "dropdown-toggle"]
    assert dropdown_toggle_classes(color="primary", size="sm") == [
        "btn",
        "btn-primary",
        "btn-sm",
        "dropdown-toggle",
    ]
    assert dropdown_toggle_classes(color="link", caret=False) == ["btn", "btn-link"]
    assert dropdown_toggle_classes(nav=True) == ["nav-link", "dropdown-toggle"]
    assert dropdown_toggle_classes(nav=True, caret=False) == ["nav-link"]
    with pytest.raises(ValueError, match="color"):
        dropdown_toggle_classes(color="rainbow")
    with pytest.raises(ValueError, match="size"):
        dropdown_toggle_classes(size="xl")


def test_dropdown_menu_classes() -> None:
    assert dropdown_menu_classes() == ["dropdown-menu"]
    assert dropdown_menu_classes(menu_variant="light") == ["dropdown-menu"]
    assert dropdown_menu_classes(menu_variant="dark", align_end=True) == [
        "dropdown-menu",
        "dropdown-menu-dark",
        "dropdown-menu-end",
    ]
    with pytest.raises(ValueError, match="menu_variant"):
        dropdown_menu_classes(menu_variant="blue")


def test_dropdown_item_inner_classes() -> None:
    assert dropdown_item_inner_classes() == ["dropdown-item"]
    assert dropdown_item_inner_classes(disabled=True, active=True) == [
        "dropdown-item",
        "disabled",
        "active",
    ]
    assert dropdown_item_inner_classes(header=True) == ["dropdown-header"]
    assert dropdown_item_inner_classes(divider=True) == ["dropdown-divider"]


def test_dropdown_menu_compat_rejects_native_and_removed_props() -> None:
    with pytest.raises(UnsupportedPropError, match="is_open"):
        DbcDropdownMenu(is_open=True)
    with pytest.raises(UnsupportedPropError, match="on_item_click"):
        DbcDropdownMenu(on_item_click=lambda: None)
    with pytest.raises(UnsupportedPropError, match="right"):
        DbcDropdownMenu(right=True)
    with pytest.raises(UnsupportedPropError, match="addon_type"):
        DbcDropdownMenu(addon_type="prepend")
    with pytest.raises(ValueError, match="direction"):
        DropdownMenu(direction="sideways")


def test_dropdown_menu_item_header_divider_conflict() -> None:
    with pytest.raises(PropConflictError, match="header"):
        DropdownMenuItem(header=True, divider=True)


def test_collapse_structural_classes() -> None:
    assert collapse_structural_classes() == ["collapse"]
    assert collapse_structural_classes(navbar=True) == ["collapse", "navbar-collapse"]
    assert collapse_structural_classes(dimension="width") == ["collapse", "collapse-horizontal"]
    with pytest.raises(ValueError, match="dimension"):
        collapse_structural_classes(dimension="depth")
    with pytest.raises(ValueError, match="dimension"):
        Collapse(dimension="depth")
    with pytest.raises(UnsupportedPropError, match="dimension"):
        DbcCollapse(dimension="width")


def test_fade_structural_classes_and_is_open_rejected() -> None:
    assert fade_structural_classes() == ["fade"]
    assert fade_structural_classes(is_in=True) == ["fade", "show"]
    with pytest.raises(UnsupportedPropError, match="is_open"):
        Fade(is_open=True)
    with pytest.raises(UnsupportedPropError, match="is_open"):
        DbcFade(is_open=True)


def test_accordion_structural_classes() -> None:
    assert accordion_structural_classes() == ["accordion"]
    assert accordion_structural_classes(flush=True) == ["accordion", "accordion-flush"]


def test_generate_accordion_item_ids() -> None:
    assert generate_accordion_item_ids([]) == []
    assert generate_accordion_item_ids([None, None]) == ["item-0", "item-1"]
    assert generate_accordion_item_ids(["x", None]) == ["x", "item-0"]
    assert generate_accordion_item_ids([None, "item-0"]) == ["item-1", "item-0"]
    assert generate_accordion_item_ids(["a", "b"]) == ["a", "b"]


def test_resolve_accordion_active() -> None:
    ids = ["a", "b"]
    assert (
        resolve_accordion_active(None, always_open=False, item_ids=ids, default_first=True) == "a"
    )
    assert (
        resolve_accordion_active(None, always_open=False, item_ids=ids, default_first=False) is None
    )
    assert resolve_accordion_active(None, always_open=True, item_ids=ids, default_first=True) == [
        "a"
    ]
    assert resolve_accordion_active(None, always_open=True, item_ids=ids, default_first=False) == []
    assert resolve_accordion_active("a", always_open=True, item_ids=ids) == ["a"]
    assert resolve_accordion_active(["a", "z"], always_open=True, item_ids=ids) == ["a"]
    assert resolve_accordion_active(["a", "b"], always_open=False, item_ids=ids) == "a"
    assert resolve_accordion_active("missing", always_open=False, item_ids=ids) is None
    assert resolve_accordion_active("missing", always_open=True, item_ids=ids) == []


def test_modal_dialog_classes() -> None:
    assert modal_dialog_classes() == ["modal-dialog"]
    assert modal_dialog_classes(size="lg", centered=True, scrollable=True) == [
        "modal-dialog",
        "modal-lg",
        "modal-dialog-centered",
        "modal-dialog-scrollable",
    ]
    assert modal_dialog_classes(fullscreen=True) == ["modal-dialog", "modal-fullscreen"]
    assert modal_dialog_classes(fullscreen="sm-down") == [
        "modal-dialog",
        "modal-fullscreen-sm-down",
    ]
    assert modal_dialog_classes(fullscreen="modal-fullscreen-md-down") == [
        "modal-dialog",
        "modal-fullscreen-md-down",
    ]
    assert modal_dialog_classes(dialog_class_name="extra") == ["modal-dialog", "extra"]


def test_offcanvas_structural_classes() -> None:
    assert offcanvas_structural_classes(placement="start") == ["offcanvas", "offcanvas-start"]
    assert offcanvas_structural_classes(placement="end") == ["offcanvas", "offcanvas-end"]
    assert offcanvas_structural_classes(placement="top") == ["offcanvas", "offcanvas-top"]
    assert offcanvas_structural_classes(placement="bottom") == ["offcanvas", "offcanvas-bottom"]
    with pytest.raises(ValueError, match="placement"):
        offcanvas_structural_classes(placement="middle")
    with pytest.raises(ValueError, match="placement"):
        Offcanvas(placement="middle")


@pytest.mark.user
async def test_modal_renders(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with Modal(is_open=True):
            ModalBody("ngbs-modal-hello")

    await user.open("/")
    await user.should_see("ngbs-modal-hello")


@pytest.mark.user
async def test_collapse_renders(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        Collapse("ngbs-collapse-hello", is_open=True)

    await user.open("/")
    await user.should_see("ngbs-collapse-hello")


@pytest.mark.user
async def test_accordion_renders(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with Accordion():
            AccordionItem(title="ngbs-accordion-hello")

    await user.open("/")
    await user.should_see("ngbs-accordion-hello")
