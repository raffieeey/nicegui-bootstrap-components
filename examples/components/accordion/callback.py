"""Accordion that reports the open item through on_change."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        selected = ui.label("Item selected: item-1")

        def on_change(event: object) -> None:
            value = getattr(event, "value", event)
            selected.set_text(f"Item selected: {value}")

        with bs.accordion(active_item="item-1", on_change=on_change):
            with bs.accordion_item(title="Item 1", item_id="item-1"):
                ui.label("This is the content of the first section")
            with bs.accordion_item(title="Item 2", item_id="item-2"):
                ui.label("This is the content of the second section")
            with bs.accordion_item(title="Item 3", item_id="item-3"):
                ui.label("This is the content of the third section")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Accordion callback")
