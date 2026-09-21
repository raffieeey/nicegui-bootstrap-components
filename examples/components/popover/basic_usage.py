from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        button = ui.button("Status")
        bs.popover(
            bs.PopoverHeader("Publish state"),
            bs.PopoverBody("This record is ready to publish."),
            target=button,
            placement="bottom",
            trigger="click",
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
