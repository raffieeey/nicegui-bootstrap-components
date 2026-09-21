"""Top navbar layout with two pages."""

from __future__ import annotations

from nicegui import ui

from nicegui_bootstrap_components import bs


def build_layout(path: str, heading: str, paragraph: str) -> None:
    with bs.scope():
        with bs.navbar_simple(brand="App", color="dark", dark=True):
            bs.nav_link("Home", href="/", active=path == "/")
            bs.nav_link("Page 2", href="/page-2", active=path == "/page-2")
        with bs.container(), bs.card():
            ui.label(heading).classes("h4")
            ui.label(paragraph)


@ui.page("/")
def page_home() -> None:
    build_layout("/", "Home", "This is the home page.")


@ui.page("/page-2")
def page_two() -> None:
    build_layout("/page-2", "Page 2", "This is the second page.")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Navbar")
