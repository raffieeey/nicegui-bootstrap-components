from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo():
    with bs.scope():
        with bs.dropdown_menu(label="More", direction="up", align_end=True):
            bs.dropdown_menu_item("Profile", href="/profile")
            bs.dropdown_menu_item("Settings", href="/settings")
            bs.dropdown_menu_item(header=True, children="Account")
            bs.dropdown_menu_item("Sign out")

        with bs.dropdown_menu(label="Site", in_navbar=True, caret=True):
            bs.dropdown_menu_item("Docs", href="/docs")
            bs.dropdown_menu_item("Blog", href="/blog")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Dropdown Menu — Direction and navbar")
