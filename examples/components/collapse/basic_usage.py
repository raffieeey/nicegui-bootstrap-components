from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.collapse(is_open=True):
        ui.label("This panel is visible on first render.")
        ui.label("Put any grouping content inside the collapse.")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Collapse basic usage")
