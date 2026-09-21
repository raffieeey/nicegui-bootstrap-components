"""Horizontal alignment set through the row's justify option."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    cell_class = "border border-primary rounded p-2"
    with bs.scope(), bs.container():
        for justify in ("start", "center", "end", "between", "around"):
            with bs.row(justify=justify):
                with bs.col(width=4, class_name=cell_class):
                    ui.label("One of two columns")
                with bs.col(width=4, class_name=cell_class):
                    ui.label("One of two columns")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Horizontal alignment")
