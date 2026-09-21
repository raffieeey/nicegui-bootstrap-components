"""Interactive Iris clustering and filter view."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from nicegui import ui

from nicegui_bootstrap_components import bs

try:
    import matplotlib
except ImportError:
    matplotlib = None

_IRIS: list[tuple[float, float, float, float, str]] = [
    (5.1, 3.5, 1.4, 0.2, "setosa"),
    (4.9, 3.0, 1.4, 0.2, "setosa"),
    (4.7, 3.2, 1.3, 0.2, "setosa"),
    (4.6, 3.1, 1.5, 0.2, "setosa"),
    (5.0, 3.6, 1.4, 0.2, "setosa"),
    (5.4, 3.9, 1.7, 0.4, "setosa"),
    (4.6, 3.4, 1.4, 0.3, "setosa"),
    (5.0, 3.4, 1.5, 0.2, "setosa"),
    (4.4, 2.9, 1.4, 0.2, "setosa"),
    (4.9, 3.1, 1.5, 0.1, "setosa"),
    (7.0, 3.2, 4.7, 1.4, "versicolor"),
    (6.4, 3.2, 4.5, 1.5, "versicolor"),
    (6.9, 3.1, 4.9, 1.5, "versicolor"),
    (5.5, 2.3, 4.0, 1.3, "versicolor"),
    (6.5, 2.8, 4.6, 1.5, "versicolor"),
    (5.7, 2.8, 4.5, 1.3, "versicolor"),
    (6.3, 3.3, 4.7, 1.6, "versicolor"),
    (4.9, 2.4, 3.3, 1.0, "versicolor"),
    (6.6, 2.9, 4.6, 1.3, "versicolor"),
    (5.2, 2.7, 3.9, 1.4, "versicolor"),
    (6.3, 3.3, 6.0, 2.5, "virginica"),
    (5.8, 2.7, 5.1, 1.9, "virginica"),
    (7.1, 3.0, 5.9, 2.1, "virginica"),
    (6.3, 2.9, 5.6, 1.8, "virginica"),
    (6.5, 3.0, 5.8, 2.2, "virginica"),
    (7.6, 3.0, 6.6, 2.1, "virginica"),
    (4.9, 2.5, 4.5, 1.7, "virginica"),
    (7.3, 2.9, 6.3, 1.8, "virginica"),
    (6.7, 2.5, 5.8, 1.8, "virginica"),
    (7.2, 3.6, 6.1, 2.5, "virginica"),
]


def _load_iris() -> list[tuple[float, float, float, float, str]]:
    """Load a local CSV when present; otherwise return the embedded sample."""
    path = Path(__file__).resolve().parent / "data.csv"
    if path.is_file():
        loaded: list[tuple[float, float, float, float, str]] = []
        with path.open(newline="", encoding="utf-8") as handle:
            for raw in csv.reader(handle):
                if len(raw) < 5:
                    continue
                try:
                    loaded.append(
                        (float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3]), raw[4].strip())
                    )
                except ValueError:
                    continue
        if loaded:
            return loaded
    return list(_IRIS)


def _k_means(points: list[list[float]], k: int, rounds: int = 15) -> list[int]:
    """Tiny deterministic k-means; centroids start at even sample intervals."""
    if not points:
        return []
    k = max(1, min(int(k), len(points)))
    centroids = [points[min(i * len(points) // k, len(points) - 1)][:] for i in range(k)]
    labels = [0] * len(points)
    dims = len(points[0])
    for _ in range(rounds):
        for i, point in enumerate(points):
            best = 0
            best_dist = 0.0
            for cluster in range(k):
                dist = 0.0
                for dim in range(dims):
                    diff = point[dim] - centroids[cluster][dim]
                    dist += diff * diff
                if cluster == 0 or dist < best_dist:
                    best = cluster
                    best_dist = dist
            labels[i] = best
        for cluster in range(k):
            members = [points[i] for i, lab in enumerate(labels) if lab == cluster]
            if not members:
                continue
            centroids[cluster] = [
                sum(member[dim] for member in members) / len(members) for dim in range(dims)
            ]
    return labels


def demo() -> None:
    with bs.scope(), bs.container(), bs.card():
        bs.label("Iris k-means")
        with bs.row():
            with bs.col(md=4):
                bs.label("Species")
                species = bs.select(
                    options=["all", "setosa", "versicolor", "virginica"],
                    value="all",
                )
            with bs.col(md=4):
                bs.label("k")
                k_slider = ui.slider(min=1, max=3, step=1, value=3)
        host = bs.col()

        def render(*_args: Any) -> None:
            choice = str(getattr(species, "value", "all") or "all")
            raw_k = getattr(k_slider, "value", 3)
            k = int(raw_k) if raw_k is not None else 3
            rows = _load_iris()
            if choice != "all":
                rows = [row for row in rows if row[4] == choice]
            host.clear()
            if not rows:
                with host:
                    bs.label("No rows for this filter.")
                return
            points = [[row[0], row[1], row[2], row[3]] for row in rows]
            labels = _k_means(points, k)
            with host:
                if matplotlib is not None and hasattr(ui, "matplotlib"):
                    plot = ui.matplotlib(figsize=(6, 4))
                    ax = plot.figure.gca()
                    palette = ("#4C78A8", "#F58518", "#54A24B", "#E45756")
                    face = [palette[lab % len(palette)] for lab in labels]
                    ax.scatter([row[2] for row in rows], [row[3] for row in rows], c=face)
                    ax.set_xlabel("petal length")
                    ax.set_ylabel("petal width")
                    plot.figure.tight_layout()
                    plot.update()
                else:
                    with bs.table():
                        for row, lab in zip(rows, labels, strict=True):
                            bs.label(f"{row[4]} cluster {lab}")

        bs.button("Cluster", on_click=render)
        render()


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Iris k-means")
