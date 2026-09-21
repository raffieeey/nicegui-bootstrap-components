from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope():
        bs.breadcrumb(
            items=[
                {"label": "Home", "href": "/"},
                {"label": "Library", "href": "/library"},
                {"label": "Data", "active": True},
            ],
            item_class_name="small",
            item_style={"fontWeight": "500"},
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Breadcrumb item styling")
