from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope():
        with bs.collapse(is_open=True, dimension="width"):
            ui.label("Revealed along the width axis.")

        with bs.collapse(is_open=True, navbar=True, id="main-nav-collapse"):
            ui.label("Navbar links go here.")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Collapse dimension and navbar")
