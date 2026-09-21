"""Pill-shaped badges."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.badge("Primary", color="primary", pill=True).classes("me-1")
        bs.badge("Secondary", color="secondary", pill=True).classes("me-1")
        bs.badge("Success", color="success", pill=True).classes("me-1")
        bs.badge("Warning", color="warning", pill=True).classes("me-1")
        bs.badge("Danger", color="danger", pill=True).classes("me-1")
        bs.badge("Info", color="info", pill=True).classes("me-1")
        bs.badge("Light", text_color="dark", color="light", pill=True).classes("me-1")
        bs.badge("Dark", color="dark", pill=True)


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Pill badges")
