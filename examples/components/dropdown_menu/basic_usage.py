from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope(), bs.dropdown_menu(label="Actions", color="primary"):
        bs.dropdown_menu_item("Edit")
        bs.dropdown_menu_item("Duplicate")
        bs.dropdown_menu_item(divider=True)
        bs.dropdown_menu_item("Delete")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Dropdown Menu — Basic usage")
