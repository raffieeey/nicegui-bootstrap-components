"""Button color variants."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope(), bs.row():
        for color in (
            "primary",
            "secondary",
            "success",
            "danger",
            "warning",
            "info",
            "light",
            "dark",
        ):
            bs.button(color.capitalize(), color=color)


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Button colors")
