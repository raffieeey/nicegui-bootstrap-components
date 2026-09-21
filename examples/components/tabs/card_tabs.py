"""Tabs with card styling."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        tabs = bs.tabs(card=True)
        with tabs:
            bs.tab(label="Home")
            bs.tab(label="Profile")
            bs.tab(label="Contact")
        ui.label("Active tab is tracked on the tabs component.")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Card tabs")
