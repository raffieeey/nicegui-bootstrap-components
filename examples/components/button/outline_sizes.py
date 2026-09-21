"""Button outline and size variants."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        with bs.row():
            bs.button("Small outline", color="primary", outline=True, size="sm")
            bs.button("Default outline", color="secondary", outline=True)
            bs.button("Large outline", color="success", outline=True, size="lg")
        with bs.row():
            bs.button("Small", color="primary", size="sm")
            bs.button("Default", color="primary")
            bs.button("Large", color="primary", size="lg")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Button outline and sizes")
