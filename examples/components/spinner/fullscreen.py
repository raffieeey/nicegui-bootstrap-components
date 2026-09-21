"""Fullscreen spinner toggled by a button."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        spinner = bs.spinner(fullscreen=True, color="primary")
        spinner.visible = False

        def toggle() -> None:
            spinner.visible = not spinner.visible

        bs.button("Toggle fullscreen spinner", on_click=toggle)


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Fullscreen spinner")
