"""Multipage navigation with a simple sidebar and active links."""

from __future__ import annotations

from nicegui import ui

from nicegui_bootstrap_components import bs


def _link(title: str, path: str, current: str) -> None:
    bs.nav_link(title, href=path, active=current == path)


def _page(path: str, heading: str, body: str) -> None:
    with bs.scope(), bs.container(), bs.row():
        with bs.col(md=3):
            bs.label("Sidebar")
            _link("Home", "/", path)
            _link("Page 2", "/page2", path)
            _link("Page 3", "/page3", path)
        with bs.col(md=9), bs.card():
            bs.label(heading)
            bs.label(body)


def demo() -> None:
    @ui.page("/")
    def home() -> None:
        _page("/", "Home", "Placeholder content for the home page.")

    @ui.page("/page2")
    def page2() -> None:
        _page("/page2", "Page 2", "Placeholder content for page 2.")

    @ui.page("/page3")
    def page3() -> None:
        _page("/page3", "Page 3", "Placeholder content for page 3.")

    _page("/", "Home", "Placeholder content for the home page.")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Simple Sidebar")
