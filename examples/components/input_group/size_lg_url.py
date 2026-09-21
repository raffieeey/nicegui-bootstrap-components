from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope(), bs.input_group(size="lg"):
        bs.input_group_text("https://")
        bs.input(placeholder="example.com")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="InputGroup size lg URL")
