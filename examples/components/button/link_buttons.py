from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        bs.button("Open docs", color="info", outline=True, href="/docs")
        bs.button(
            "Export",
            color="secondary",
            href="/export.csv",
            download="export.csv",
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Button link buttons")
