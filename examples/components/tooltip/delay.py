from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        icon = ui.button("?")
        bs.tooltip(
            "What is this field?",
            target=icon,
            placement="bottom",
            trigger="focus",
            delay=150,
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Tooltip focus delay")
