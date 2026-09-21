from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        notice = bs.toast(
            "Record saved",
            is_open=True,
            icon="check",
            class_name="position-fixed top-0 end-0 m-3",
        )
        ui.button("Save", on_click=notice.show)


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
