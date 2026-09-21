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
                {
                    "src": _slide("#1a365d", "#2b6cb0"),
                    "alt": "Harbor at dawn",
                    "header": "Welcome",
                    "caption": "A short caption for the first slide.",
                },
                {
                    "src": _slide("#276749", "#48bb78"),
                    "alt": "Forest trail",
                    "header": "Explore",
                    "caption": "Call out a second point.",
                },
                {
                    "src": _slide("#4a3728", "#c05621"),
                    "alt": "Studio interior",
                    "header": "Build",
                    "caption": "Close with a third idea.",
                },
            ]
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Carousel basic")
