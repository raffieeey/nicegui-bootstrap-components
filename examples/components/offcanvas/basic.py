from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with (
        bs.scope(),
        bs.offcanvas(is_open=True, placement="start", backdrop=True).style("padding:24px"),
    ):
        ui.label("Filters")
        ui.label("Search")
        ui.input()
        ui.button("Apply")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Offcanvas basic")
