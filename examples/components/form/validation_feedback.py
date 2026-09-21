from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope(), bs.form(novalidate=True):
        bs.label("Email", html_for="email")
        bs.input(id="email", type="email", invalid=True)
        bs.form_feedback("Enter a valid email.", type="invalid")
        bs.form_text("We only use this to send receipts.", color="muted")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Form validation feedback")
