from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope(), bs.progress():
        bs.progress(value=25, color="success", striped=True, class_name="w-25")
        bs.progress(value=50, color="info", animated=True, class_name="w-25")
        bs.progress(value=75, color="warning", class_name="w-50")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
