"""Badges with an overridden text color."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.badge("Primary", text_color="primary").classes("me-1")
        bs.badge("Secondary", text_color="secondary").classes("me-1")
        bs.badge("Success", text_color="success").classes("me-1")
        bs.badge("Warning", text_color="warning").classes("me-1")
        bs.badge("Danger", text_color="danger").classes("me-1")
        bs.badge("Info", text_color="info").classes("me-1")
        bs.badge("Light", text_color="light", color="dark").classes("me-1")
        bs.badge("Dark", text_color="dark")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Badge text colors")
