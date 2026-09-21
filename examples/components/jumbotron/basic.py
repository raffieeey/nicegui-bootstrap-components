from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.card(class_name="p-5 mb-4 bg-body-tertiary rounded-3"):
        ui.label("Hello, world.").classes("fs-1 fw-bold")
        ui.label("A large callout built from Card and padding utilities.")
        bs.button("Learn more", color="primary")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
