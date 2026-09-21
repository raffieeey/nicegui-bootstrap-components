"""Column width options: fixed spans and automatically sized columns."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    cell_class = "border border-primary rounded p-2"
    with bs.scope(), bs.container():
        with bs.row(), bs.col(width=6, class_name=cell_class):
            ui.label("A single, half-width column")
        with bs.row(), bs.col(width="auto", class_name=cell_class):
            ui.label("An automatically sized column")
        with bs.row():
            with bs.col(width=3, class_name=cell_class):
                ui.label("One of three columns")
            with bs.col(class_name=cell_class):
                ui.label("One of three columns")
            with bs.col(width=3, class_name=cell_class):
                ui.label("One of three columns")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Column widths")
