from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        with bs.button_group(size="sm"):
            bs.button("Day", color="primary")
            bs.button("Week", color="primary", outline=True)
            bs.button("Month", color="primary", outline=True)

        with bs.button_group(size="lg", vertical=True):
            bs.button("Top", color="secondary")
            bs.button("Middle", color="secondary")
            bs.button("Bottom", color="secondary")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Button group size and vertical", reload=False)
