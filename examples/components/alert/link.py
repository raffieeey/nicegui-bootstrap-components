"""Alerts with a color-matched link."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        with bs.alert(color="primary") as first:
            ui.label("This is a primary alert with an ").classes("d-inline")
            ui.link("example link", "#").classes("alert-link")
        with bs.alert(color="danger"):
            ui.label("This is a danger alert with an ").classes("d-inline")
            ui.link("example link", "#").classes("alert-link")
        del first


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Alert links")
