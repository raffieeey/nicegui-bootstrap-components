"""A row with the gutter spacing removed."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    cell_class = "border border-primary rounded p-2"
    with bs.scope(), bs.container(), bs.row(g=0):
        with bs.col(class_name=cell_class):
            ui.label("One of three columns")
        with bs.col(class_name=cell_class):
            ui.label("One of three columns")
        with bs.col(class_name=cell_class):
            ui.label("One of three columns")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Row without gutters")
