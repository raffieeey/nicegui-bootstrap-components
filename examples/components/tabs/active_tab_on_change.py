from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    def on_change(_event: object) -> None:
        ui.notify("tab changed")

    with bs.scope():
        bs.Tabs(
            bs.Tab("Overview"),
            bs.Tab("Metrics"),
            active_tab="Overview",
            on_change=on_change,
            class_name="nav-pills",
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
