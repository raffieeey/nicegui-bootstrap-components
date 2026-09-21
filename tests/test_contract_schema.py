"""L1 schema checks for the frozen DBC 2.0.4 component contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_CONTRACT_PATH = (
    _REPO_ROOT / "src" / "nicegui_bootstrap_components" / "contracts" / "dbc-2.0.4.json"
)
ROOT_CONTRACT_PATH = _REPO_ROOT / "contracts" / "dbc-2.0.4.json"
_CANDIDATES = (
    PACKAGE_CONTRACT_PATH,
    ROOT_CONTRACT_PATH,
)


def _resolve_contract() -> Path | None:
    return next((p for p in _CANDIDATES if p.is_file()), None)


KNOWN_MODULES = frozenset(
    {
        "accordion",
        "alert",
        "badge",
        "breadcrumb",
        "button",
        "buttongroup",
        "card",
        "carousel",
        "collapse",
        "dropdownmenu",
        "fade",
        "form",
        "input",
        "layout",
        "listgroup",
        "modal",
        "nav",
        "offcanvas",
        "pagination",
        "placeholder",
        "popover",
        "progress",
        "spinner",
        "table",
        "tabs",
        "toast",
        "tooltip",
    }
)

_DISPOSITION_KEYS = frozenset({"compat", "native", "note"})


@pytest.fixture(scope="module")
def contract() -> dict[str, Any]:
    """Load the DBC 2.0.4 contract JSON from the first existing candidate path."""
    path = _resolve_contract()
    if path is None:
        pytest.fail(
            "DBC 2.0.4 contract not found; checked "
            f"{PACKAGE_CONTRACT_PATH} and {ROOT_CONTRACT_PATH}"
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        pytest.fail(f"Invalid JSON in {path}: {exc}")


def _prop_items(props: Any, owner: str) -> list[dict[str, Any]]:
    if isinstance(props, dict):
        items = list(props.values())
    else:
        assert isinstance(props, list), f"{owner} props must be list or dict"
        items = props
    return items


def _walk_props(props: Any, owner: str) -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    for prop in _prop_items(props, owner):
        assert isinstance(prop, dict), f"{owner} prop is not an object"
        prop_name = prop.get("name")
        path = f"{owner}.{prop_name}"
        found.append((path, prop))
        shape = prop.get("shape")
        if shape is None:
            continue
        assert isinstance(shape, dict), f"{path} shape must be an object"
        found.extend(_walk_props(shape, f"{path}.shape"))
    return found


def _assert_prop_schema(path: str, prop: dict[str, Any]) -> None:
    assert isinstance(prop.get("name"), str) and prop["name"], f"{path} missing name"
    dbc_type = prop.get("dbc_type")
    assert isinstance(dbc_type, str) and dbc_type, f"{path} dbc_type must be a non-empty string"
    assert "description" in prop, f"{path} missing description"
    assert isinstance(prop.get("required"), bool), f"{path} required must be bool"
    assert isinstance(prop.get("dash_only"), bool), f"{path} dash_only must be bool"
    disp = prop.get("disposition")
    assert isinstance(disp, dict), f"{path} missing disposition object"
    assert set(disp.keys()) == _DISPOSITION_KEYS, (
        f"{path} disposition keys={set(disp.keys())!r} (expected exactly {_DISPOSITION_KEYS})"
    )


def test_json_load(contract: dict[str, Any]) -> None:
    assert isinstance(contract, dict)


def test_count_equals_len_components(contract: dict[str, Any]) -> None:
    assert "count" in contract
    assert "components" in contract
    assert isinstance(contract["components"], dict)
    assert contract["count"] == len(contract["components"]), (
        f"count={contract['count']!r} != len(components)={len(contract['components'])}"
    )


def test_component_count_is_66(contract: dict[str, Any]) -> None:
    assert len(contract["components"]) == 66, (
        f"expected 66 components, got {len(contract['components'])}"
    )
    assert contract["count"] == 66


def test_every_component_has_known_module(contract: dict[str, Any]) -> None:
    assert contract["components"], "components mapping must not be empty"
    for name, component in contract["components"].items():
        assert isinstance(component, dict), name
        module = component.get("module")
        assert module is not None, f"{name} module is null; needs curation"
        assert module in KNOWN_MODULES, f"{name} module={module!r} not in known DBC modules"


def test_every_prop_has_disposition(contract: dict[str, Any]) -> None:
    n_props = 0
    for name, component in contract["components"].items():
        assert "props" in component, f"{name} missing props"
        for path, prop in _walk_props(component["props"], name):
            n_props += 1
            disp = prop.get("disposition")
            assert isinstance(disp, dict), f"{path} missing disposition object"
            assert set(disp.keys()) == _DISPOSITION_KEYS, (
                f"{path} disposition keys={set(disp.keys())!r} "
                f"(expected exactly {_DISPOSITION_KEYS})"
            )
    assert n_props > 0, "expected at least one prop in the contract"


def test_contract_component_and_prop_schema(contract: dict[str, Any]) -> None:
    components = contract["components"]
    assert isinstance(components, dict)
    assert components, "components mapping must not be empty"
    n_props = 0
    for name, component in components.items():
        assert isinstance(component, dict), name
        assert component.get("docstring") is not None, f"{name} docstring is null"
        assert isinstance(component["docstring"], str), f"{name} docstring must be a string"
        assert component.get("description") is not None, f"{name} description is null"
        assert isinstance(component["description"], str), f"{name} description must be a string"
        prop_names = component.get("prop_names")
        assert isinstance(prop_names, list), f"{name} prop_names must be a list"
        module = component.get("module")
        assert module is not None, f"{name} module is null; needs curation"
        assert module in KNOWN_MODULES, f"{name} module={module!r} not in known DBC modules"
        dash_only_props = component.get("dash_only_props")
        assert isinstance(dash_only_props, list), f"{name} dash_only_props must be a list"
        aliases = component.get("aliases")
        assert isinstance(aliases, dict), f"{name} aliases must be a dict"
        defaults = component.get("defaults")
        assert defaults is None or isinstance(defaults, dict), (
            f"{name} defaults must be a dict or null"
        )
        assert "props" in component, f"{name} missing props"
        for path, prop in _walk_props(component["props"], name):
            n_props += 1
            _assert_prop_schema(path, prop)
    assert n_props > 0, "expected at least one prop in the contract"
