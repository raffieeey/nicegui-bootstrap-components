"""Vertical alignment set on the row and on individual columns."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    cell_class = "border border-primary rounded p-2"
    with bs.scope(), bs.container():
        for align in ("start", "center", "end"):
            with bs.row(align=align):
                with bs.col(class_name=cell_class):
                    ui.label("One of three columns")
                with bs.col(class_name=cell_class):
                    ui.label("One of three columns")
                with bs.col(class_name=cell_class):
                    ui.label("One of three columns")
        with bs.row():
            with bs.col(align="start", class_name=cell_class):
                ui.label("One of three columns")
            with bs.col(align="center", class_name=cell_class):
                ui.label("One of three columns")
            with bs.col(align="end", class_name=cell_class):
                ui.label("One of three columns")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Vertical alignment")
