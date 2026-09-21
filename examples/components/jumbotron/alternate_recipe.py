from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.card(class_name="p-5 border-0 bg-primary text-white rounded-0"):
        ui.label("Ship the next release").classes("fs-2 fw-bold")
        ui.label("Status, highlights, and a single primary action.")
        bs.button("Open changelog", color="light")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
