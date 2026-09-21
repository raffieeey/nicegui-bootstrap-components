"""Dismissible and colored alerts."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.alert("Primary alert", color="primary")
        bs.alert("Success, dismissable", color="success", dismissable=True)
        bs.alert("Warning, dismissable", color="warning", dismissable=True)
        bs.alert("Danger, dismissable", color="danger", dismissable=True)
        bs.alert("Info, dismissable", color="info", dismissable=True)


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Dismissible alerts")
