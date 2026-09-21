from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope(), bs.button_group():
        bs.button("Left", color="secondary")
        bs.button("Middle", color="secondary")
        bs.button("Right", color="secondary")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Button group basic", reload=False)
