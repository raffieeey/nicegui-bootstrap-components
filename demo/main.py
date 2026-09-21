"""Demo service that serves gallery examples on isolated NiceGUI routes."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from nicegui import ui

from nicegui_bootstrap_components import StyleMode, setup

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from demo.registry import (  # noqa: E402
    ExampleEntry,
    dedupe,
    load_manifest,
    module_path_for,
)

__all__ = [
    "main",
    "register_examples",
]

_DEFAULT_MANIFEST = _REPO_ROOT / "examples" / "manifest.yaml"


def register_examples(app_routes_collector: list[ExampleEntry]) -> int:
    """Register one NiceGUI page per examples manifest entry.

    Example modules are imported when a page is visited, not at registration
    time. Returns the number of example routes registered.
    """
    entries = dedupe(load_manifest(_DEFAULT_MANIFEST))
    app_routes_collector.extend(entries)
    for entry in entries:
        _register_example_page(entry)
    _register_index_page(list(app_routes_collector))
    return len(entries)


def _register_example_page(entry: ExampleEntry) -> None:
    @ui.page(entry.route)
    def example_page() -> None:
        _render_example(entry)


def _render_example(entry: ExampleEntry) -> None:
    module_name = module_path_for(entry)
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        ui.label(f"Failed to import example {entry.id}: {exc}")
        return
    demo_fn = getattr(module, "demo", None)
    if callable(demo_fn):
        demo_fn()
        return
    # Page-function templates (multi-page examples) define ``page_*``
    # functions instead of a ``demo()``. Render the first one directly on
    # this route so the template is still previewable in the gallery.
    pages = [
        fn
        for name, fn in sorted(vars(module).items())
        if name.startswith("page_")
        and callable(fn)
        and not _is_class(fn)
        and _accepts_no_required_args(fn)
    ]
    if not pages:
        ui.label(f"Example {entry.id} does not define a demo() function.")
        return
    pages[0]()


def _is_class(obj: object) -> bool:
    return isinstance(obj, type)


def _accepts_no_required_args(fn: object) -> bool:
    """True when ``fn`` can be called with no arguments."""
    import inspect

    try:
        signature = inspect.signature(fn)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    for parameter in signature.parameters.values():
        if (
            parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
            and parameter.default is parameter.empty
        ):
            return False
        if parameter.kind is parameter.KEYWORD_ONLY and parameter.default is parameter.empty:
            return False
    return True


def _register_index_page(entries: list[ExampleEntry]) -> None:
    @ui.page("/examples/")
    def examples_index() -> None:
        for entry in entries:
            ui.link(entry.title, entry.route)


def main() -> None:
    """Start the examples demo service."""
    setup(mode=StyleMode.MIXED)
    register_examples([])
    ui.run(
        title="NiceGUI Bootstrap Components — Examples",
        language="en",
        port=8080,
        show=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
