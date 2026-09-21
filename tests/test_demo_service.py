"""L1 tests for the demo service wiring."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest
from nicegui import Client, app
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from demo.main import (  # noqa: E402
    _DEFAULT_MANIFEST,
    _register_example_page,
    register_examples,
)
from demo.registry import ExampleEntry, load_manifest  # noqa: E402

pytest_plugins = ["nicegui.testing.plugin"]


def _registered_route_paths() -> set[str]:
    """Return paths registered on the FastAPI app and NiceGUI page map."""
    paths: set[str] = set()
    for route in app.routes:
        path = getattr(route, "path", None)
        if isinstance(path, str):
            paths.add(path)
    for path in Client.page_routes.values():
        if isinstance(path, str):
            paths.add(path)
    return paths


def test_register_examples_registers_all_manifest_entries() -> None:
    expected = len(load_manifest(_DEFAULT_MANIFEST))
    collector: list[ExampleEntry] = []
    count = register_examples(collector)
    assert expected == 107
    assert count == expected
    assert len(collector) == expected
    ids = [entry.id for entry in collector]
    assert len(ids) == len(set(ids))


def test_register_examples_registers_pages() -> None:
    register_examples([])
    paths = _registered_route_paths()
    assert "/examples/iris/" in paths


@pytest.mark.user
async def test_index_page_renders_example_links(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    collector: list[ExampleEntry] = []
    register_examples(collector)
    assert len(collector) >= 2
    await user.open("/examples/")
    await user.should_see(collector[0].title)
    await user.should_see(collector[1].title)


@pytest.mark.user
async def test_render_example_reports_missing_import(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    entry = ExampleEntry(
        id="missing_import_wiring",
        title="Missing Import",
        route="/examples/missing_import_wiring/",
        source="no_such_demo_example_module.py",
        components=[],
        extras=[],
        version="",
    )
    _register_example_page(entry)
    await user.open(entry.route)
    await user.should_see("Failed to import example missing_import_wiring:")


def test_grid_only_gallery_preview_does_not_call_setup() -> None:
    """demo() is what the gallery renders; it must not reconfigure stylesheets."""
    example_path = _REPO_ROOT / "examples" / "components" / "layout" / "grid_only.py"
    source = example_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    demo_fn = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "demo"
    )
    for child in ast.walk(demo_fn):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if isinstance(func, ast.Name):
            assert func.id != "setup"
        elif isinstance(func, ast.Attribute):
            assert func.attr != "setup"

    assert "theme=themes.GRID" in source
    assert "StyleMode.UNSCOPED" in source
    assert 'if __name__ in {"__main__", "__mp_main__"}' in source

    docs = (_REPO_ROOT / "docs_site" / "components" / "layout.md").read_text(encoding="utf-8")
    docs_flat = re.sub(r"\s+", " ", docs)
    assert "setup(mode=StyleMode.UNSCOPED, theme=themes.GRID)" in docs
    assert "{{example:examples/components/layout/grid_only.py:demo}}" in docs
    assert "setup(mode=StyleMode.MIXED)" in docs
    assert "this preview is not a grid-only theme" in docs_flat
