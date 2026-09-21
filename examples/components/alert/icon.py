"""Alerts with leading icons."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        with bs.alert(color="info").classes("d-flex align-items-center"):
            ui.icon("bi bi-info-circle-fill").classes("me-2")
            ui.label("An example info alert with an icon")
        with bs.alert(color="success").classes("d-flex align-items-center"):
            ui.icon("bi bi-check-circle-fill").classes("me-2")
            ui.label("An example success alert with an icon")
        with bs.alert(color="warning").classes("d-flex align-items-center"):
            ui.icon("bi bi-exclamation-triangle-fill").classes("me-2")
            ui.label("An example warning alert with an icon")
        with bs.alert(color="danger").classes("d-flex align-items-center"):
            ui.icon("bi bi-x-octagon-fill").classes("me-2")
            ui.label("An example danger alert with an icon")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Alerts with icons")
