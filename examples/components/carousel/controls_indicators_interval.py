from urllib.parse import quote

from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def _slide(fill: str, accent: str) -> str:
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='900' height='280'>"
        f"<rect width='900' height='280' fill='{fill}'/>"
        f"<circle cx='780' cy='70' r='110' fill='{accent}'/>"
        "</svg>"
    )
    return "data:image/svg+xml," + quote(svg)


def demo():
    with bs.scope():
        bs.carousel(
            items=[
                {"src": _slide("#2a4365", "#3182ce"), "alt": "One", "header": "One"},
                {"src": _slide("#553c2a", "#dd6b20"), "alt": "Two", "caption": "Second slide"},
            ],
            controls=True,
            indicators=True,
            interval=False,
            active_index=0,
            slide=True,
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Carousel controls indicators interval")
