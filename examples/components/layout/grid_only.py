"""Grid-only stylesheet: Bootstrap's grid without the full theme."""

from nicegui import ui

from nicegui_bootstrap_components import bs, themes
from nicegui_bootstrap_components.assets import StyleMode, setup


def demo() -> None:
    # Body only — do not call setup here (process-wide, already applied).
    # Standalone grid-only CSS is loaded in ``__main__``; the gallery stays MIXED.
    # Grid-only CSS has no border/padding utilities, and package style props
    # require dicts, so apply a CSS string via NiceGUI .style() on a nested element.
    cell_style = (
        "border: 1px solid #0d6efd; border-radius: 0.375rem; "
        "padding: 0.5rem; width: 100%; box-sizing: border-box;"
    )
    with bs.scope(), bs.container(), bs.row():
        with bs.col(width=6), ui.element().style(cell_style):
            ui.label("half-width")
        with bs.col(width=6), ui.element().style(cell_style):
            ui.label("half-width")


if __name__ in {"__main__", "__mp_main__"}:
    # Load only the grid CSS instead of the full Bootstrap stylesheet.
    setup(mode=StyleMode.UNSCOPED, theme=themes.GRID)
    demo()
    ui.run(title="Grid only")
