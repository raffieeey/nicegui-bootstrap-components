"""A counter badge nested inside a button."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.button(
            [
                "Notifications",
                bs.badge("4", color="light", text_color="primary").classes("ms-1"),
            ],
            color="primary",
        )


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Badges")
