"""Vertical stacks with and without a gap between items."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        with bs.stack():
            ui.label("This stack has no gaps").classes("border rounded p-2")
            ui.label("Next item").classes("border rounded p-2")
            ui.label("Last item").classes("border rounded p-2")
        ui.separator()
        with bs.stack(gap=3):
            ui.label("This stack has gaps").classes("border rounded p-2")
            ui.label("Next item").classes("border rounded p-2")
            ui.label("Last item").classes("border rounded p-2")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Stacking objects")
