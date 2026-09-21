from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        bs.button("Outline", color="primary", outline=True)
        bs.button("Small", color="secondary", size="sm")
        bs.button("Large", color="secondary", size="lg")
        bs.button("Disabled", color="primary", disabled=True)


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Button outline size state")
