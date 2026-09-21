"""Badges rendered as links."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.badge("Primary", href="#", color="primary").classes("me-1 text-decoration-none")
        bs.badge("Secondary", href="#", color="secondary").classes("me-1 text-decoration-none")
        bs.badge("Success", href="#", color="success").classes("me-1 text-decoration-none")
        bs.badge("Warning", href="#", color="warning").classes("me-1 text-decoration-none")
        bs.badge("Danger", href="#", color="danger").classes("me-1 text-decoration-none")
        bs.badge("Info", href="#", color="info").classes("me-1 text-decoration-none")
        bs.badge("Light", href="#", text_color="dark", color="light").classes(
            "me-1 text-decoration-none"
        )
        bs.badge("Dark", href="#", color="dark").classes("text-decoration-none")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Link badges")
