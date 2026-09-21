"""Alert containing a heading, paragraphs, and a divider."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope(), bs.alert(color="success"):
        ui.label("Well done!").classes("alert-heading h4")
        ui.label(
            "This is a success alert with loads of extra text in it. So much "
            "that you can see how spacing within an alert works with this "
            "kind of content."
        )
        ui.separator()
        ui.label("Let's put some more text down here, but remove the bottom margin").classes("mb-0")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Alert content")
