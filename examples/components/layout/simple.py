"""Basic layout with a container, row, and two columns."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope(), bs.container(), bs.row():
        with bs.col(width=12, md=6):
            ui.label("Primary column").classes("border rounded p-2")
        with bs.col(width=12, md=6):
            ui.label("Secondary column").classes("border rounded p-2")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Basic layout")
