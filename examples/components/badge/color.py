"""Badges across the contextual background colors."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.badge("Primary", color="primary").classes("me-1")
        bs.badge("Secondary", color="secondary").classes("me-1")
        bs.badge("Success", color="success").classes("me-1")
        bs.badge("Warning", color="warning").classes("me-1")
        bs.badge("Danger", color="danger").classes("me-1")
        bs.badge("Info", color="info").classes("me-1")
        bs.badge("Light", text_color="dark", color="light").classes("me-1")
        bs.badge("Dark", color="dark")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Badge colors")
