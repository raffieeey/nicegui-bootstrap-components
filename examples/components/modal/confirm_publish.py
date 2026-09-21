from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope(), bs.modal(size="lg", is_open=True):
        with bs.modal_header():
            bs.modal_title("Confirm publish")
        with bs.modal_body():
            ui.label("This will make the draft visible to everyone.")
        with bs.modal_footer():
            bs.button("Cancel", color="secondary")
            bs.button("Publish")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Modal confirm publish")
