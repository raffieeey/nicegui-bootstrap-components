from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope():
        bs.pagination(max_value=10, active_page=1, size="sm")
        bs.pagination(max_value=10, active_page=2, size="lg", class_name="justify-content-end")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
