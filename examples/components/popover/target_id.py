from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        ui.button("Details").props("id=details-trigger")
        bs.popover(
            bs.PopoverBody("More information"),
            target="details-trigger",
            placement="top",
            trigger="click",
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
