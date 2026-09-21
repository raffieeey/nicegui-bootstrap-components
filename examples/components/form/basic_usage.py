from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    def on_submit() -> None:
        ui.notify("Saved")

    with bs.scope(), bs.form(novalidate=True, on_submit=on_submit):
        bs.label("Name", html_for="name")
        bs.input(id="name", placeholder="Your name", required=True)
        bs.form_text("The name other people will see.")
        bs.button("Save")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Form basic usage")
