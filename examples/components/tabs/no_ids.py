"""Tabs without explicit ids."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope(), bs.tabs():
        bs.tab(label="Alpha")
        bs.tab(label="Beta")
        bs.tab(label="Gamma")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Tabs without ids")
