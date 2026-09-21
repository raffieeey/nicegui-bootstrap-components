"""Column behaviour overridden per screen size."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    cell_class = "border border-primary rounded p-2"
    with bs.scope(), bs.container():
        with bs.row():
            with bs.col(md=4, class_name=cell_class):
                ui.label("One of three columns")
            with bs.col(md=4, class_name=cell_class):
                ui.label("One of three columns")
            with bs.col(md=4, class_name=cell_class):
                ui.label("One of three columns")
        with bs.row():
            with bs.col(width=6, lg=3, class_name=cell_class):
                ui.label("One of four columns")
            with bs.col(width=6, lg=3, class_name=cell_class):
                ui.label("One of four columns")
            with bs.col(width=6, lg=3, class_name=cell_class):
                ui.label("One of four columns")
            with bs.col(width=6, lg=3, class_name=cell_class):
                ui.label("One of four columns")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Grid breakpoints per size")
