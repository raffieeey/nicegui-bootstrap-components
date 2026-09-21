from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        bs.toast(
            "Ready",
            is_open=True,
            class_name="position-fixed bottom-0 end-0 m-3",
        )
        ui.label("Workspace")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
