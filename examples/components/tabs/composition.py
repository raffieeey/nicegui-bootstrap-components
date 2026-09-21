from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        bs.Tabs(
            bs.Tab("Team"),
            bs.Tab("Billing"),
            bs.Tab("Audit log"),
            active_tab="Team",
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
