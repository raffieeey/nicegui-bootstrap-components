from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope(), bs.form_floating():
        bs.input(placeholder="name@example.com", id="flt")
        bs.label("Email address", html_for="flt")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Form floating label")
