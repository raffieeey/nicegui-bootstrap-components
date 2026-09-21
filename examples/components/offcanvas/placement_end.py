from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.offcanvas(placement="end", is_open=True, backdrop=True):
        ui.label("Inspector")
        ui.button("Close details")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Offcanvas placement")
