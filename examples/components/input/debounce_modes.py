"""Input debounce modes."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        last = ui.label("Last event:")

        def on_bool(*_args: object) -> None:
            last.set_text("Last event: boolean debounce")

        def on_int(*_args: object) -> None:
            last.set_text("Last event: integer debounce")

        ui.label("Boolean debounce")
        bs.input(placeholder="Type here", debounce=True, on_change=on_bool)
        ui.label("Integer debounce (500 ms)")
        # int debounce applies to the native surface
        bs.input(placeholder="Type here", debounce=500, on_change=on_int)


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Input debounce modes")
