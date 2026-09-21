"""Alert that dismisses itself after a duration."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        alert = bs.alert(
            "Hello! I am an auto-dismissing alert!",
            is_open=True,
            duration=4000,
        )

        def toggle() -> None:
            alert.set_value(True)

        bs.button("Toggle", on_click=toggle).classes("me-1")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Auto-dismissing alert")
