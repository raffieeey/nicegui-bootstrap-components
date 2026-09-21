"""Stacks combined with Bootstrap spacing utilities."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        with bs.stack(direction="horizontal", gap=3):
            ui.label("Start").classes("border rounded p-2")
            ui.label("Middle (ms-auto)").classes("ms-auto border rounded p-2")
            ui.label("End").classes("border rounded p-2")
        ui.separator()
        with bs.stack(direction="horizontal", gap=3):
            ui.label("Start").classes("border rounded p-2")
            ui.label("Middle (mx-auto)").classes("mx-auto border rounded p-2")
            ui.label("End").classes("border rounded p-2")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Stack spacers")
