from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        bs.button("Save", color="primary", on_click=lambda: ui.notify("Saved"))
        bs.button("Cancel", color="secondary")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Button basic usage")
