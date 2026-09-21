"""L1 tests for the API documentation generator."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

apidoc = importlib.import_module("docs_site._hooks.apidoc")
PROPERTY_COLUMNS = apidoc.PROPERTY_COLUMNS
RENAMES = apidoc.RENAMES
expand_directives = apidoc.expand_directives
on_page_markdown = apidoc.on_page_markdown
render_apidoc_table = apidoc.render_apidoc_table
render_code_example = apidoc.render_code_example
render_example_demo = apidoc.render_example_demo

PACKAGE_CONTRACT_PATH = (
    _ROOT / "src" / "nicegui_bootstrap_components" / "contracts" / "dbc-2.0.4.json"
)
ROOT_CONTRACT_PATH = _ROOT / "contracts" / "dbc-2.0.4.json"
_CANDIDATES = (
    PACKAGE_CONTRACT_PATH,
    ROOT_CONTRACT_PATH,
)


def _resolve_contract() -> Path | None:
    return next((p for p in _CANDIDATES if p.is_file()), None)


_CONTRACT_PATH = _resolve_contract()


@pytest.fixture
def contract() -> dict[str, Any]:
    return {
        "components": {
            "Button": {
                "props": [
                    {"name": "class_name", "type_raw": "str | None", "default": None},
                    {"name": "color", "type_raw": "str", "default": "primary"},
                    {"name": "debounce", "type_raw": "int", "default": 0},
                ]
            },
            "Input": {
                "props": [
                    {"name": "loading_state", "dbc_type": "dict", "default": None},
                    {"name": "n_clicks", "type_raw": "int", "default": 0},
                    {"name": "key", "type_raw": "str | None", "default": None},
                ]
            },
        }
    }


def _row_for(table: str, property_name: str) -> str:
    needle = f"| {property_name} |"
    for line in table.splitlines():
        if needle in line:
            return line
    raise AssertionError(f"no row for {property_name!r} in {table!r}")


def test_property_columns() -> None:
    assert PROPERTY_COLUMNS == [
        "Property",
        "Type",
        "Default",
        "DBC 2.0.4 name",
        "Support (native)",
        "Support (compat)",
    ]
    assert RENAMES["class_name"] == "className"
    assert RENAMES["className"] == "class_name"
    assert RENAMES["is_open"] == "isOpen"
    assert RENAMES["hide_arrow"] == "hideArrow"


def test_table_six_columns_and_deterministic_order(contract: dict[str, Any]) -> None:
    table = render_apidoc_table("Button", contract)
    lines = table.splitlines()
    header_cells = [cell.strip() for cell in lines[0].strip("|").split("|")]
    assert header_cells == PROPERTY_COLUMNS
    assert lines[0].count("|") == 7
    data_lines = lines[2:]
    expected = ["class_name", "color", "debounce"]
    assert len(data_lines) == len(expected)
    for name, line in zip(expected, data_lines, strict=True):
        assert f"| {name} |" in line


def test_rename_mapping_in_dbc_column(contract: dict[str, Any]) -> None:
    table = render_apidoc_table("Button", contract)
    row = _row_for(table, "class_name")
    assert "| className |" in row


def test_support_defaults_dash_only_and_extension(contract: dict[str, Any]) -> None:
    button = render_apidoc_table("Button", contract)
    assert "| supported | supported |" in _row_for(button, "color")
    assert "| extension | unsupported |" in _row_for(button, "debounce")

    inp = render_apidoc_table("Input", contract)
    assert "| unsupported | unsupported |" in _row_for(inp, "loading_state")
    assert "| adapted | adapted |" in _row_for(inp, "n_clicks")
    assert "| unsupported | unsupported |" in _row_for(inp, "key")


def test_render_code_example(tmp_path: Path) -> None:
    rel = "examples/hello.py"
    path = tmp_path / rel
    path.parent.mkdir(parents=True)
    path.write_text("x = 1\n", encoding="utf-8")
    fenced = render_code_example(rel, repo_root=str(tmp_path))
    assert fenced.startswith("```python\n")
    assert fenced.endswith("```")
    assert "x = 1\n" in fenced


def test_render_example_demo_slices_function(tmp_path: Path) -> None:
    rel = "demo_mod.py"
    (tmp_path / rel).write_text(
        '"""module doc."""\n'
        "\n"
        "def demo() -> int:\n"
        "    return 1\n"
        "\n"
        "def other() -> int:\n"
        "    return 2\n",
        encoding="utf-8",
    )
    fenced = render_example_demo(rel, "demo", repo_root=str(tmp_path))
    assert fenced.startswith("```python\n")
    assert "def demo() -> int:" in fenced
    assert "return 1" in fenced
    assert "other" not in fenced
    assert "return 2" not in fenced
    assert "module doc" not in fenced


def test_render_example_demo_missing_function(tmp_path: Path) -> None:
    rel = "demo_mod.py"
    (tmp_path / rel).write_text("def demo() -> int:\n    return 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="ghost"):
        render_example_demo(rel, "ghost", repo_root=str(tmp_path))


def test_missing_file_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        render_code_example("missing.py", repo_root=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        render_example_demo("missing.py", "demo", repo_root=str(tmp_path))


def test_expand_all_three_directive_forms(tmp_path: Path, contract: dict[str, Any]) -> None:
    example = tmp_path / "ex.py"
    example.write_text(
        "def demo() -> int:\n    return 1\n\ndef other() -> int:\n    return 2\n",
        encoding="utf-8",
    )
    markdown = "A {{apidoc:Button}}\nB {{code-example:ex.py}}\nC {{example:ex.py:demo}}\n"
    result = expand_directives(markdown, repo_root=str(tmp_path), contract=contract)
    assert "{{apidoc:Button}}" not in result
    assert "{{code-example:ex.py}}" not in result
    assert "{{example:ex.py:demo}}" not in result
    assert "| Property |" in result
    assert "| class_name |" in result
    assert "def demo() -> int:" in result
    assert "def other() -> int:" in result

    code_block = render_code_example("ex.py", repo_root=str(tmp_path))
    assert "def demo() -> int:" in code_block
    assert "def other() -> int:" in code_block

    demo_block = render_example_demo("ex.py", "demo", repo_root=str(tmp_path))
    assert "def demo() -> int:" in demo_block
    assert "def other" not in demo_block

    apidoc_part, rest = result.split("\nB ", 1)
    code_part, demo_part = rest.split("\nC ", 1)
    assert "| Property |" in apidoc_part
    assert "| class_name |" in apidoc_part
    assert "def demo() -> int:" in code_part
    assert "def other() -> int:" in code_part
    assert "def demo() -> int:" in demo_part
    assert "def other" not in demo_part


def test_malformed_and_unknown_directives() -> None:
    contract = {"components": {"X": {"props": []}}}
    cases = (
        ("{{apidoc}}", "apidoc"),
        ("{{apidoc:}}", "apidoc"),
        ("{{code-example}}", "code-example"),
        ("{{code-example:}}", "code-example"),
        ("{{example:foo.py}}", "example"),
        ("{{mystery:x}}", "mystery"),
        ("{{nonsense}}", "nonsense"),
        ("{{apidoc:NotAComponent}}", "NotAComponent"),
    )
    for text, name in cases:
        with pytest.raises(ValueError, match=name):
            expand_directives(text, repo_root=".", contract=contract)


def test_unknown_component_names_component(contract: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="Ghost"):
        render_apidoc_table("Ghost", contract)
    with pytest.raises(ValueError, match="Ghost"):
        expand_directives("{{apidoc:Ghost}}", repo_root=".", contract=contract)


def test_expand_apidoc_without_contract() -> None:
    note = "contract data unavailable at this build"
    assert expand_directives("{{apidoc:Button}}", repo_root=".", contract=None) == note
    assert expand_directives("{{apidoc:Button}}", repo_root=".", contract={}) == note


def test_on_page_markdown_missing_contract(tmp_path: Path) -> None:
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: test\n", encoding="utf-8")
    result = on_page_markdown(
        "{{apidoc:Button}}",
        config={"config_file_path": str(mkdocs)},
    )
    assert result == "contract data unavailable at this build"


def test_on_page_markdown_loads_contract(tmp_path: Path, contract: dict[str, Any]) -> None:
    (tmp_path / "contracts").mkdir()
    (tmp_path / "contracts" / "dbc-2.0.4.json").write_text(
        json.dumps(contract),
        encoding="utf-8",
    )
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text("site_name: test\n", encoding="utf-8")
    result = on_page_markdown(
        "{{apidoc:Button}}",
        config={"config_file_path": str(mkdocs)},
    )
    assert "| class_name |" in result
    assert "| className |" in result


@pytest.mark.skipif(
    _CONTRACT_PATH is None,
    reason="DBC 2.0.4 contract not found",
)
def test_real_contract_button() -> None:
    assert _CONTRACT_PATH is not None
    data = json.loads(_CONTRACT_PATH.read_text(encoding="utf-8"))
    components = data["components"]
    assert len(components) >= 60
    table = render_apidoc_table("Button", data)
    header_cells = [cell.strip() for cell in table.splitlines()[0].strip("|").split("|")]
    assert header_cells == PROPERTY_COLUMNS
