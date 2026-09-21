from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        bs.input(type="email", placeholder="name@example.com")
        bs.input(type="password", placeholder="Password", size="sm")
        bs.input(type="number", min=0, max=10, step=1, value=1)


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Input placeholder type size")
