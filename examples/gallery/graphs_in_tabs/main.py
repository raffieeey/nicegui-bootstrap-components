"""Charts sized correctly when shown in Bootstrap tabs."""

from __future__ import annotations

import math
from typing import Any

from nicegui import ui

from nicegui_bootstrap_components import bs

try:
    import matplotlib
except ImportError:
    matplotlib = None


def _xy(name: str) -> tuple[list[float], list[float]]:
    xs = [i / 10 for i in range(63)]
    if name == "Sine":
        return xs, [math.sin(x) for x in xs]
    if name == "Cosine":
        return xs, [math.cos(x) for x in xs]
    return xs, [0.15 * x for x in xs]


def demo() -> None:
    plots: dict[str, Any] = {}

    def draw(name: str) -> None:
        plot = plots.get(name)
        if plot is None:
            return
        fig = plot.figure
        fig.clear()
        ax = fig.gca()
        xs, ys = _xy(name)
        ax.plot(xs, ys)
        ax.set_title(name)
        fig.tight_layout()
        plot.update()

    def on_change(_event: Any = None) -> None:
        # Chart is redrawn when the tab changes so hidden panes pick up the correct size.
        value = getattr(_event, "value", None)
        if isinstance(value, str) and value in plots:
            draw(value)
            return
        for name in plots:
            draw(name)

    with bs.scope(), bs.container(), bs.tabs(on_change=on_change):
        for name in ("Sine", "Cosine", "Data"):
            with bs.tab(label=name):
                if matplotlib is not None:
                    plots[name] = ui.matplotlib(figsize=(6, 3))
                    draw(name)
                else:
                    bs.progress(value=50)


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Graphs in Tabs")
