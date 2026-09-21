"""Badges that scale with the size of their parent heading."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        for level in range(1, 7):
            with ui.element(f"h{level}").classes("d-flex align-items-center"):
                ui.label("Example heading")
                bs.badge("New", color="secondary").classes("ms-1")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Badge sizing")
