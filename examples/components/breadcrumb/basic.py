from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope():
        bs.breadcrumb(
            items=[
                {"label": "Home", "href": "/"},
                {"label": "Projects", "href": "/projects"},
                {"label": "Northwind", "active": True},
            ]
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Breadcrumb basic")
