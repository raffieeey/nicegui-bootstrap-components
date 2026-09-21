from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.nav():
        with bs.nav_item():
            bs.nav_link("Home", href="/", active=True)
        with bs.nav_item():
            bs.nav_link("Docs", href="/docs")
        with bs.nav_item():
            bs.nav_link("Blog", href="/blog")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Nav")
