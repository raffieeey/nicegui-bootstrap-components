"""Badge positioned in the corner of a button."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.button(
            [
                "Notifications",
                bs.badge(
                    "99+",
                    color="danger",
                    pill=True,
                    text_color="white",
                    class_name="position-absolute top-0 start-100 translate-middle",
                ),
            ],
            color="primary",
            class_name="position-relative",
        )


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Positioned badge")
