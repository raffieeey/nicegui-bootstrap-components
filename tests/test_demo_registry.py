"""L1 tests for the demo example registry."""

from __future__ import annotations

import sys
from pathlib import Path
from textwrap import dedent

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from demo.registry import (  # noqa: E402
    ExampleEntry,
    dedupe,
    load_manifest,
    module_path_for,
    route_for,
)


def test_load_manifest_valid(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text(
        dedent(
            """\
            examples:
              - id: iris
                title: Iris Gallery
                route: /examples/iris/
                source: examples/gallery/iris/main.py
                components:
                  - Table
                extras:
                  - pandas
                version: "1.0"
            """
        ),
        encoding="utf-8",
    )
    entries = load_manifest(path)
    assert len(entries) == 1
    entry = entries[0]
    assert entry.id == "iris"
    assert entry.title == "Iris Gallery"
    assert entry.route == "/examples/iris/"
    assert entry.source == "examples/gallery/iris/main.py"
    assert entry.components == ["Table"]
    assert entry.extras == ["pandas"]
    assert entry.version == "1.0"


def test_load_manifest_optional_fields_default(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text(
        dedent(
            """\
            - id: sidebar
              title: Simple Sidebar
              route: /examples/sidebar/
              source: examples/templates/simple_sidebar.py
            """
        ),
        encoding="utf-8",
    )
    entries = load_manifest(str(path))
    assert len(entries) == 1
    entry = entries[0]
    assert entry.components == []
    assert entry.extras == []
    assert entry.version == ""


def test_load_manifest_missing_file(tmp_path: Path) -> None:
    assert load_manifest(tmp_path / "does-not-exist.yaml") == []


def test_load_manifest_malformed_entry(tmp_path: Path) -> None:
    path = tmp_path / "manifest.yaml"
    path.write_text(
        dedent(
            """\
            - id: iris
              title: Iris Gallery
              route: /examples/iris/
            """
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="iris"):
        load_manifest(path)


def test_route_for() -> None:
    assert route_for("iris") == "/examples/iris/"
    assert route_for("simple_sidebar") == "/examples/simple_sidebar/"


def test_module_path_for() -> None:
    sidebar = ExampleEntry(
        id="simple_sidebar",
        title="Simple Sidebar",
        route="/examples/simple_sidebar/",
        source="examples/templates/simple_sidebar.py",
        components=[],
        extras=[],
        version="",
    )
    iris = ExampleEntry(
        id="iris",
        title="Iris",
        route="/examples/iris/",
        source="examples/gallery/iris/main.py",
        components=[],
        extras=[],
        version="",
    )
    assert module_path_for(sidebar) == "examples.templates.simple_sidebar"
    assert module_path_for(iris) == "examples.gallery.iris.main"


def test_dedupe_later_id_wins() -> None:
    first = ExampleEntry(
        id="iris",
        title="Old",
        route="/examples/iris/",
        source="examples/gallery/iris/main.py",
        components=[],
        extras=[],
        version="1",
    )
    other = ExampleEntry(
        id="other",
        title="Other",
        route="/examples/other/",
        source="examples/gallery/other/main.py",
        components=[],
        extras=[],
        version="1",
    )
    later = ExampleEntry(
        id="iris",
        title="New",
        route="/examples/iris/",
        source="examples/gallery/iris/main.py",
        components=["Table"],
        extras=[],
        version="2",
    )
    result = dedupe([first, other, later])
    assert [entry.id for entry in result] == ["iris", "other"]
    assert result[0].title == "New"
    assert result[0].version == "2"
    assert result[0].components == ["Table"]


def _load_real_manifest() -> list[ExampleEntry]:
    path = _REPO_ROOT / "examples" / "manifest.yaml"
    if not path.is_file():
        pytest.skip("examples/manifest.yaml is absent")
    return load_manifest(path)


def test_real_manifest_ids_are_unique() -> None:
    entries = _load_real_manifest()
    ids = [entry.id for entry in entries]
    assert len(ids) == len(set(ids))
    assert len(entries) == 107


def test_real_manifest_entries_are_complete() -> None:
    entries = _load_real_manifest()
    for entry in entries:
        assert entry.id
        assert entry.title
        assert entry.route
        assert entry.source
        assert (_REPO_ROOT / entry.source).is_file()


def test_real_manifest_routes_are_unique() -> None:
    entries = _load_real_manifest()
    routes = [entry.route for entry in entries]
    assert len(routes) == len(set(routes))
