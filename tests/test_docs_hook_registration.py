"""L1 tests for MkDocs hook registration and contract shipping."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
_CONTRACT_CANDIDATES: tuple[Path, ...] = (
    REPO_ROOT / "contracts" / "dbc-2.0.4.json",
    REPO_ROOT / "src" / "nicegui_bootstrap_components" / "contracts" / "dbc-2.0.4.json",
)

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_contract() -> dict[str, Any]:
    for path in _CONTRACT_CANDIDATES:
        if not path.is_file():
            continue
        loaded: Any = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            return loaded
    raise FileNotFoundError("DBC contract JSON was not found in either candidate location")


def _expand_directives(markdown: str, contract: dict[str, Any]) -> str:
    from docs_site._hooks.apidoc import expand_directives

    return expand_directives(markdown, repo_root=str(REPO_ROOT), contract=contract)


def test_hook_registered_in_mkdocs_yml() -> None:
    loaded: Any = yaml.safe_load((REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    hooks = loaded.get("hooks")
    assert isinstance(hooks, list)
    assert "docs_site/_hooks/apidoc.py" in hooks


def test_directive_expands_via_hook() -> None:
    result = _expand_directives("{{apidoc:Button}}", _load_contract())
    assert "| Property |" in result


def test_contract_resolvable_from_package_location() -> None:
    existing = [path for path in _CONTRACT_CANDIDATES if path.is_file()]
    assert existing, "DBC contract JSON missing from both candidate locations"
    loaded: Any = json.loads(existing[0].read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    components = loaded.get("components")
    assert isinstance(components, dict)
    assert "Button" in components


def test_unknown_component_raises() -> None:
    with pytest.raises(ValueError, match="NotAComponent"):
        _expand_directives("{{apidoc:NotAComponent}}", _load_contract())
