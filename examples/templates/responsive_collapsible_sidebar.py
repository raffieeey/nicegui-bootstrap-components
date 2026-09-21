"""Responsive sidebar hidden on small screens until a button toggles it."""

from __future__ import annotations

from nicegui import ui

from nicegui_bootstrap_components import bs

_state: dict[str, bool] = {"open": False}


def _toggle() -> None:
    _state["open"] = not _state["open"]
    build_layout.refresh()


@ui.refreshable
def build_layout(path: str, heading: str, paragraph: str) -> None:
    side_class = None if _state["open"] else "d-none d-md-block"
    with bs.scope(), bs.container():
        bs.button("Menu", on_click=_toggle, class_name="d-md-none mb-2")
        with bs.row():
            with bs.col(width=12, md=2, class_name=side_class):
                bs.nav_link("Home", href="/", active=path == "/")
                bs.nav_link("Page 2", href="/page-2", active=path == "/page-2")
                bs.nav_link("Page 3", href="/page-3", active=path == "/page-3")
            with bs.col(width=12, md=10), bs.card():
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
    ui.run(title="Responsive Collapsible Sidebar")
