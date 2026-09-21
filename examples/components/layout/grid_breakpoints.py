"""Responsive Row and Col breakpoints."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope(), bs.container():
        with bs.row():
            with bs.col(width=12, md=4):
                ui.label("col-12 col-md-4")
            with bs.col(width=12, md=4):
                ui.label("col-12 col-md-4")
            with bs.col(width=12, md=4):
                ui.label("col-12 col-md-4")
        with bs.row():
            with bs.col(width=6, md=8):
                ui.label("col-6 col-md-8")
            with bs.col(width=6, md=4):
                ui.label("col-6 col-md-4")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Grid breakpoints")
