from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        link = ui.link("Policy")
        bs.popover(
            bs.PopoverHeader("Retention"),
            bs.PopoverBody("Logs are kept for 30 days."),
            target=link,
            placement="right",
            trigger="click",
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
