"""Accordion with always_open enabled."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope(), bs.accordion(always_open=True):
        with bs.accordion_item(title="Item one"):
            ui.label("First panel.")
        with bs.accordion_item(title="Item two"):
            ui.label("Second panel.")
        with bs.accordion_item(title="Item three"):
            ui.label("Third panel.")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Accordion always open")
