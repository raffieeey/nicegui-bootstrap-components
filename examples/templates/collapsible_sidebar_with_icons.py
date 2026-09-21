"""Collapsible icon-rail sidebar layout with three pages."""

from __future__ import annotations

from nicegui import ui

from nicegui_bootstrap_components import bs

_state: dict[str, bool] = {"collapsed": False}


def _toggle() -> None:
    _state["collapsed"] = not _state["collapsed"]
    build_sidebar.refresh()


def _nav_item(icon: str, label: str, href: str, path: str, collapsed: bool) -> None:
    with bs.nav_link(href=href, active=path == href):
        ui.icon(icon)
        if not collapsed:
            ui.label(label)


@ui.refreshable
def build_sidebar(path: str) -> None:
    collapsed = _state["collapsed"]
    with bs.col(width=2):
        with bs.button(on_click=_toggle):
            ui.icon("menu")
        _nav_item("home", "Home", "/", path, collapsed)
        _nav_item("article", "Page 2", "/page-2", path, collapsed)
        _nav_item("info", "Page 3", "/page-3", path, collapsed)


def build_layout(path: str, heading: str, paragraph: str) -> None:
    with bs.scope(), bs.container(), bs.row():
        build_sidebar(path)
        with bs.col(width=10), bs.card():
            ui.label(heading).classes("h4")
            ui.label(paragraph)


@ui.page("/")
def page_home() -> None:
    build_layout("/", "Home", "This is the home page.")


@ui.page("/page-2")
def page_two() -> None:
    build_layout("/page-2", "Page 2", "This is the second page.")


@ui.page("/page-3")
def page_three() -> None:
    build_layout("/page-3", "Page 3", "This is the third page.")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Collapsible Sidebar with Icons")
