"""Horizontal stacks with and without a gap between items."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        with bs.stack(direction="horizontal"):
            ui.label("Horizontal").classes("border rounded p-2")
            ui.label("Stack").classes("border rounded p-2")
            ui.label("Without").classes("border rounded p-2")
            ui.label("Gaps").classes("border rounded p-2")
        ui.separator()
        with bs.stack(direction="horizontal", gap=3):
            ui.label("Horizontal").classes("border rounded p-2")
            ui.label("Stack").classes("border rounded p-2")
            ui.label("With").classes("border rounded p-2")
            ui.label("Gaps").classes("border rounded p-2")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Horizontal stack")
