from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STYLE_DIST = ROOT / "styles" / "dist"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import build_styles  # noqa: E402
from scripts.build_styles import scope_css  # noqa: E402

PACKAGE_DIST = ROOT / "src" / "nicegui_bootstrap_components" / "static" / "dist"
CORE_NAMES = ("bootstrap", "flatly", "darkly")
SCOPED_NAMES = tuple(f"ngbs-{name}.css" for name in CORE_NAMES) + ("ngbs-compat.css",)
UNSCOPED_NAMES = tuple(f"ngbs-{name}-unscoped.css" for name in CORE_NAMES) + (
    "ngbs-compat-unscoped.css",
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("html { color: red; }", ".ngbs { color: red; }"),
        ("body { color: red; }", ".ngbs { color: red; }"),
        (":root { --value: 1; }", ".ngbs { --value: 1; }"),
        ("html .item { color: red; }", ".ngbs .item { color: red; }"),
        ("body .item { color: red; }", ".ngbs .item { color: red; }"),
        (".btn { color: red; }", ".ngbs .btn { color: red; }"),
        (":hover { color: red; }", ".ngbs :hover { color: red; }"),
        (".btn.btn-primary { color: red; }", ".ngbs .btn.btn-primary { color: red; }"),
        (
            "*, *::before, *::after { box-sizing: border-box; }",
            ".ngbs *, .ngbs *::before, .ngbs *::after { box-sizing: border-box; }",
        ),
        (
            "html, .btn, body .item { color: red; }",
            ".ngbs, .ngbs .btn, .ngbs .item { color: red; }",
        ),
        (
            ":root, [data-bs-theme=light] { --value: 1; }",
            ".ngbs, .ngbs[data-bs-theme=light] { --value: 1; }",
        ),
        (
            "[data-bs-theme=dark] { --value: 1; }",
            ".ngbs[data-bs-theme=dark] { --value: 1; }",
        ),
        (
            '[data-bs-theme="dark"] { --value: 1; }',
            '.ngbs[data-bs-theme="dark"] { --value: 1; }',
        ),
        (
            "[data-bs-theme=dark i] { --value: 1; }",
            ".ngbs[data-bs-theme=dark i] { --value: 1; }",
        ),
        (
            '[data-bs-theme="dark" i] { --value: 1; }',
            '.ngbs[data-bs-theme="dark" i] { --value: 1; }',
        ),
        ("html body { color: red; }", ".ngbs { color: red; }"),
        (":root body { color: red; }", ".ngbs { color: red; }"),
        ("body>.x { color: red; }", ".ngbs>.x { color: red; }"),
        ("body.x { color: red; }", ".ngbs.x { color: red; }"),
        (
            "body:has(.modal-open) .x { color: red; }",
            ".ngbs:has(.modal-open) .x { color: red; }",
        ),
    ],
)
def test_scope_selector_map(source: str, expected: str) -> None:
    assert scope_css(source) == expected


def test_media_rules_are_scoped() -> None:
    source = "@media (min-width: 1px) { body .item { color: red; } }"
    assert scope_css(source) == "@media (min-width: 1px) { .ngbs .item { color: red; } }"


def test_keyframes_are_untouched() -> None:
    source = "@keyframes fade { from { opacity: 0; } to { opacity: 1; } }"
    assert scope_css(source) == source


def test_font_face_is_untouched() -> None:
    source = '@font-face { font-family: "Example"; src: url(example.woff2); }'
    assert scope_css(source) == source


def test_overlay_selector_is_preserved() -> None:
    output = scope_css(".ngbs-overlay .modal { display: block; }")
    assert ".ngbs .ngbs-overlay .modal" in output
    assert ":root-overlay" not in output


def test_no_document_root_descendant_is_emitted() -> None:
    output = scope_css("html { color: red; } body { color: blue; }")
    assert ".ngbs html" not in output
    assert ".ngbs body" not in output


def test_selector_map_refuses_a_descendant_anchor() -> None:
    with pytest.raises(RuntimeError, match=r"\.ngbs \.ngbs"):
        scope_css(".ngbs .ngbs { color: red; }")


def test_declarations_are_byte_preserved() -> None:
    source = '.btn { color: rgb(1 2 3 / 50%); --raw: "a:b;"; }'
    output = scope_css(source)
    assert output == '.ngbs .btn { color: rgb(1 2 3 / 50%); --raw: "a:b;"; }'


def _read_artifact(directory: Path, name: str) -> str:
    path = directory / name
    assert path.is_file(), f"missing built stylesheet: {path}"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("name", SCOPED_NAMES)
def test_built_scoped_stylesheet_invariants(name: str) -> None:
    css = _read_artifact(STYLE_DIST, name)
    assert "sourceMappingURL" not in css
    selector_start = r"(?m)(?:^|[{},])\s*"
    assert re.search(selector_start + r"html(?:\s*(?:[{.#:\[>+~]|$))", css) is None
    assert re.search(selector_start + r":root(?:\s*(?:[{.#:\[>+~]|$))", css) is None
    assert re.search(selector_start + r"body(?:\s*(?:[{.#:\[>+~]|$))", css) is None
    assert re.search(r"(?m)(?:^|[{},])\s*body\.[-\w]+", css) is None
    assert re.search(r"\.ngbs\s+(?:html|body)(?![-\w])", css) is None
    assert ":root-overlay" not in css
    if name == "ngbs-bootstrap.css":
        assert ".ngbs .modal" in css


@pytest.mark.parametrize("name", UNSCOPED_NAMES)
def test_built_unscoped_stylesheet_invariants(name: str) -> None:
    css = _read_artifact(STYLE_DIST, name)
    assert "sourceMappingURL" not in css
    assert ".ngbs " not in css
    assert ".ngbs" not in css
    assert ":root-overlay" not in css
    if name.startswith("ngbs-bootstrap"):
        assert ":root" in css


def test_built_artifacts_match_package_tree() -> None:
    assert STYLE_DIST.is_dir(), f"missing build output directory: {STYLE_DIST}"
    assert PACKAGE_DIST.is_dir(), f"missing package output directory: {PACKAGE_DIST}"
    style_files = sorted(path.name for path in STYLE_DIST.iterdir() if path.is_file())
    package_files = sorted(path.name for path in PACKAGE_DIST.iterdir() if path.is_file())
    assert style_files == package_files
    for name in style_files:
        assert (STYLE_DIST / name).read_bytes() == (PACKAGE_DIST / name).read_bytes()


def test_build_is_deterministic_without_redownloading(monkeypatch: pytest.MonkeyPatch) -> None:
    cache_files = [
        build_styles.SOURCE_CACHE_DIR / spec.cache_filename for spec in build_styles.SOURCE_SPECS
    ]
    if not all(path.is_file() for path in cache_files):
        pytest.skip("source cache is not warm")

    def fail_download(_spec: object) -> bytes:
        raise AssertionError("build attempted to download a warm source cache")

    monkeypatch.setattr(build_styles, "_download_source", fail_download)

    def snapshot() -> dict[str, bytes]:
        snapshot_data: dict[str, bytes] = {}
        for directory in (STYLE_DIST, PACKAGE_DIST):
            for path in sorted(path for path in directory.iterdir() if path.is_file()):
                snapshot_data[f"{directory.name}/{path.name}"] = path.read_bytes()
        return snapshot_data

    before = snapshot()
    build_styles.build()
    first = snapshot()
    build_styles.build()
    second = snapshot()
    assert before == first == second
