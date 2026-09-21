"""Dash Bootstrap Components compatibility surface (PascalCase sibling types)."""

from __future__ import annotations

import importlib
from typing import Any

from .._base import make_surface_classes
from ..bs._actions import DbcButton as Button
from ..bs._actions import DbcButtonGroup as ButtonGroup
from ..bs._layout import DbcCol as Col
from ..bs._layout import DbcContainer as Container
from ..bs._layout import DbcRow as Row
from ..bs._layout import DbcStack as Stack

__all__ = ["Button", "ButtonGroup", "Col", "Container", "Row", "Stack"]


def _compat_class(module_name: str, name: str) -> type[Any]:
    module = importlib.import_module(module_name)
    dname = f"Dbc{name}"
    existing = getattr(module, dname, None)
    if existing is not None:
        return existing
    impl = getattr(module, f"_{name}Impl", None)
    if impl is not None:
        _native, compat = make_surface_classes(impl)
        return compat
    raise AttributeError(
        f"{module_name} must export {dname} or _{name}Impl so dbc.{name} is a sibling type"
    )


def _try_compat(module_name: str, name: str) -> type[Any] | None:
    try:
        return _compat_class(module_name, name)
    except (ImportError, AttributeError):
        return None


for _mod, _name in (
    ("nicegui_bootstrap_components.bs._overlays", "Accordion"),
    ("nicegui_bootstrap_components.bs._overlays", "AccordionItem"),
    ("nicegui_bootstrap_components.bs._overlays", "Collapse"),
    ("nicegui_bootstrap_components.bs._overlays", "DropdownMenu"),
    ("nicegui_bootstrap_components.bs._overlays", "DropdownMenuItem"),
    ("nicegui_bootstrap_components.bs._overlays", "Fade"),
    ("nicegui_bootstrap_components.bs._overlays", "Modal"),
    ("nicegui_bootstrap_components.bs._overlays", "ModalBody"),
    ("nicegui_bootstrap_components.bs._overlays", "ModalFooter"),
    ("nicegui_bootstrap_components.bs._overlays", "ModalHeader"),
    ("nicegui_bootstrap_components.bs._overlays", "ModalTitle"),
    ("nicegui_bootstrap_components.bs._overlays", "Offcanvas"),
    ("nicegui_bootstrap_components.bs._alert_spinner", "Alert"),
    ("nicegui_bootstrap_components.bs._alert_spinner", "Spinner"),
    ("nicegui_bootstrap_components.bs._content", "Badge"),
    ("nicegui_bootstrap_components.bs._content", "Card"),
    ("nicegui_bootstrap_components.bs._content", "CardBody"),
    ("nicegui_bootstrap_components.bs._content", "CardFooter"),
    ("nicegui_bootstrap_components.bs._content", "CardGroup"),
    ("nicegui_bootstrap_components.bs._content", "CardHeader"),
    ("nicegui_bootstrap_components.bs._content", "CardImg"),
    ("nicegui_bootstrap_components.bs._content", "CardImgOverlay"),
    ("nicegui_bootstrap_components.bs._content", "CardLink"),
    ("nicegui_bootstrap_components.bs._content", "ListGroup"),
    ("nicegui_bootstrap_components.bs._content", "ListGroupItem"),
    ("nicegui_bootstrap_components.bs._content", "Placeholder"),
    ("nicegui_bootstrap_components.bs._content", "Progress"),
    ("nicegui_bootstrap_components.bs._content", "Table"),
    ("nicegui_bootstrap_components.bs._nav", "Breadcrumb"),
    ("nicegui_bootstrap_components.bs._nav", "Nav"),
    ("nicegui_bootstrap_components.bs._nav", "NavItem"),
    ("nicegui_bootstrap_components.bs._nav", "NavLink"),
    ("nicegui_bootstrap_components.bs._nav", "Pagination"),
    ("nicegui_bootstrap_components.bs._navbar", "Navbar"),
    ("nicegui_bootstrap_components.bs._navbar", "NavbarBrand"),
    ("nicegui_bootstrap_components.bs._navbar", "NavbarSimple"),
    ("nicegui_bootstrap_components.bs._navbar", "NavbarToggler"),
    ("nicegui_bootstrap_components.bs._carousel", "Carousel"),
    ("nicegui_bootstrap_components.bs._choices", "Checkbox"),
    ("nicegui_bootstrap_components.bs._choices", "Checklist"),
    ("nicegui_bootstrap_components.bs._choices", "RadioButton"),
    ("nicegui_bootstrap_components.bs._choices", "RadioItems"),
    ("nicegui_bootstrap_components.bs._choices", "Select"),
    ("nicegui_bootstrap_components.bs._choices", "Switch"),
    ("nicegui_bootstrap_components.bs._forms", "Form"),
    ("nicegui_bootstrap_components.bs._forms", "FormFeedback"),
    ("nicegui_bootstrap_components.bs._forms", "FormFloating"),
    ("nicegui_bootstrap_components.bs._forms", "FormText"),
    ("nicegui_bootstrap_components.bs._forms", "InputGroup"),
    ("nicegui_bootstrap_components.bs._forms", "InputGroupText"),
    ("nicegui_bootstrap_components.bs._forms", "Label"),
    ("nicegui_bootstrap_components.bs._inputs", "Input"),
    ("nicegui_bootstrap_components.bs._inputs", "Textarea"),
    ("nicegui_bootstrap_components.bs._tabs", "Tab"),
    ("nicegui_bootstrap_components.bs._tabs", "Tabs"),
    ("nicegui_bootstrap_components.bs._toast", "Toast"),
    ("nicegui_bootstrap_components.bs._tooltip_popover", "Popover"),
    ("nicegui_bootstrap_components.bs._tooltip_popover", "PopoverBody"),
    ("nicegui_bootstrap_components.bs._tooltip_popover", "PopoverHeader"),
    ("nicegui_bootstrap_components.bs._tooltip_popover", "Tooltip"),
):
    _cls = _try_compat(_mod, _name)
    if _cls is not None:
        globals()[_name] = _cls
        __all__.append(_name)

__all__.sort()
