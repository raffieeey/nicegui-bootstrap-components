from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.list_group(flush=True):
        bs.list_group_item("Profile")
        bs.list_group_item("Billing")
        bs.list_group_item("Sign out")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="ListGroup flush")
