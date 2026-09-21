"""Public surface contract: the 66 components across bs and dbc."""

from __future__ import annotations

from nicegui_bootstrap_components import bs, dbc

NAMES: tuple[str, ...] = (
    "Accordion",
    "AccordionItem",
    "Alert",
    "Badge",
    "Breadcrumb",
    "Button",
    "ButtonGroup",
    "Card",
    "CardBody",
    "CardFooter",
    "CardGroup",
    "CardHeader",
    "CardImg",
    "CardImgOverlay",
    "CardLink",
    "Carousel",
    "Checkbox",
    "Checklist",
    "Col",
    "Collapse",
    "Container",
    "DropdownMenu",
    "DropdownMenuItem",
    "Fade",
    "Form",
    "FormFeedback",
    "FormFloating",
    "FormText",
    "Input",
    "InputGroup",
    "InputGroupText",
    "Label",
    "ListGroup",
    "ListGroupItem",
    "Modal",
    "ModalBody",
    "ModalFooter",
    "ModalHeader",
    "ModalTitle",
    "Nav",
    "NavItem",
    "NavLink",
    "Navbar",
    "NavbarBrand",
    "NavbarSimple",
    "NavbarToggler",
    "Offcanvas",
    "Pagination",
    "Placeholder",
    "Popover",
    "PopoverBody",
    "PopoverHeader",
    "Progress",
    "RadioButton",
    "RadioItems",
    "Row",
    "Select",
    "Spinner",
    "Stack",
    "Switch",
    "Tab",
    "Table",
    "Tabs",
    "Textarea",
    "Toast",
    "Tooltip",
)


def _pascal_to_snake(name: str) -> str:
    chars: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index > 0:
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


def test_all_66_on_both_surfaces() -> None:
    assert len(NAMES) == 66
    assert len(set(NAMES)) == 66
    assert set(NAMES) <= set(bs.__all__)
    assert set(NAMES) <= set(dbc.__all__)
    assert list(dbc.__all__) == list(NAMES)


def test_native_compat_are_sibling_types() -> None:
    for name in NAMES:
        native = getattr(bs, name)
        compat = getattr(dbc, name)
        assert native is not compat
        assert native.component_name == name
        assert compat.component_name == name


def test_scope_is_native_only() -> None:
    assert "scope" in bs.__all__
    assert "Scope" in bs.__all__
    assert "scope" not in dbc.__all__
    assert "Scope" not in dbc.__all__
    assert hasattr(dbc, "scope") is False
    assert hasattr(dbc, "Scope") is False


def test_aliases_exist_on_native_surface() -> None:
    for name in NAMES:
        alias = _pascal_to_snake(name)
        assert alias in bs.__all__
        assert getattr(bs, alias) is getattr(bs, name)


def test_surface_identity_for_existing_pairs() -> None:
    assert bs.Button is not dbc.Button
    assert bs.Col is not dbc.Col
    assert bs.Tooltip is not dbc.Tooltip
    assert bs.Tooltip.__module__.endswith("_tooltip_popover")
    assert dbc.Tooltip.__module__.endswith("_tooltip_popover")
