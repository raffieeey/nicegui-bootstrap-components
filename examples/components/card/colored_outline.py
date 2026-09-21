from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        bs.card("A primary outline card.", body=True, color="primary", outline=True)
        bs.card("A dark inverse card.", body=True, color="dark", inverse=True)


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Card colored outline")
