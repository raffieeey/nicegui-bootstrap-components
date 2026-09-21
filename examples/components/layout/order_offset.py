"""Reordering and offsetting columns through the width dictionary form."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    cell_class = "border border-primary rounded p-2"
    with bs.scope(), bs.container():
        with bs.row(), bs.col(width={"size": 6, "offset": 3}, class_name=cell_class):
            ui.label("A single, half-width column")
        with bs.row():
            with bs.col(width={"size": 3, "order": "last", "offset": 1}, class_name=cell_class):
                ui.label("The last of three columns")
            with bs.col(width={"size": 3, "order": 1, "offset": 2}, class_name=cell_class):
                ui.label("The first of three columns")
            with bs.col(width={"size": 3, "order": 5}, class_name=cell_class):
                ui.label("The second of three columns")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Order and offset")
