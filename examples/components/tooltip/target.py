from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        ui.button("Help").props("id=help-button")
        bs.tooltip(
            "Opens the handbook",
            target="help-button",
            placement="right",
            trigger="hover",
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Tooltip target id")
