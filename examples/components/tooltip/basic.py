from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        button = ui.button("Hints")
        bs.tooltip(
            "Keyboard shortcut: /",
            target=button,
            placement="top",
            trigger="hover",
            delay=200,
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Tooltip basic usage")
