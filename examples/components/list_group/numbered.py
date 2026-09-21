from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.list_group(numbered=True):
        bs.list_group_item("Create a project")
        bs.list_group_item("Invite the team")
        bs.list_group_item("Ship the first build")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="ListGroup numbered")
