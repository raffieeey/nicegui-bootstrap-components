from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.list_group():
        bs.list_group_item("Inbox")
        bs.list_group_item("Drafts")
        bs.list_group_item("Sent")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="ListGroup basic")
