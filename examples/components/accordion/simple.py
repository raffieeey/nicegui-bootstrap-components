"""Accordion with rich content per panel."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope(), bs.accordion():
        with bs.accordion_item(title="Item 1"):
            ui.label("This is the content of the first section")
            bs.button("Click here")
        with bs.accordion_item(title="Item 2"):
            ui.label("This is the content of the second section")
            bs.button("Don't click me!", color="danger")
        with bs.accordion_item(title="Item 3"):
            ui.label("This is the content of the third section")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Accordion")
