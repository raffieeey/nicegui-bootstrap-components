from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.nav(vertical=True):
        with bs.nav_item():
            bs.nav_link("Overview", href="/overview", active=True)
        with bs.nav_item():
            bs.nav_link("Metrics", href="/metrics")
        with bs.nav_item():
            bs.nav_link("Logs", href="/logs")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Nav vertical")
