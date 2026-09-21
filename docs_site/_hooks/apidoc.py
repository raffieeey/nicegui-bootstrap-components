"""Markdown API-doc tables, example fences, and the MkDocs page hook."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

__all__ = [
    "PROPERTY_COLUMNS",
    "RENAMES",
    "SUPPORT",
    "expand_directives",
    "on_page_markdown",
    "render_apidoc_table",
    "render_code_example",
    "render_example_demo",
]

PROPERTY_COLUMNS = [
    "Property",
    "Type",
    "Default",
    "DBC 2.0.4 name",
    "Support (native)",
    "Support (compat)",
]

# Bidirectional map of library Python names and DBC 2.0.4 prop names.
RENAMES: dict[str, str] = {
    "class_name": "className",
    "className": "class_name",
    "is_open": "isOpen",
    "isOpen": "is_open",
    "hide_arrow": "hideArrow",
    "hideArrow": "hide_arrow",
}

_LIBRARY_TO_DBC: dict[str, str] = {
    "class_name": "className",
    "is_open": "isOpen",
    "hide_arrow": "hideArrow",
}

# Pure Dash artifacts with no library analogue.
_DASH_ONLY_UNSUPPORTED: frozenset[str] = frozenset(
    {
        "persistence",
        "persisted_props",
        "persistedProps",
        "persistence_type",
        "persistenceType",
        "loading_state",
        "loadingState",
        "key",
        "n_clicks_timestamp",
        "nClicksTimestamp",
    }
)

# Dash props that the library exposes in adapted form.
_DASH_ONLY_ADAPTED: frozenset[str] = frozenset({"n_clicks", "nClicks"})

# Native-only extensions rejected on the compat surface.
_NATIVE_EXTENSIONS: frozenset[str] = frozenset(
    {
        "debounce",
        "read_only",
        "readOnly",
        "on_blur",
        "on_focus",
        "on_enter",
        "on_input",
    }
)


def _build_support() -> dict[str, tuple[str, str]]:
    mapping: dict[str, tuple[str, str]] = {}
    for name in _DASH_ONLY_UNSUPPORTED:
        mapping[name] = ("unsupported", "unsupported")
    for name in _DASH_ONLY_ADAPTED:
        mapping[name] = ("adapted", "adapted")
    for name in _NATIVE_EXTENSIONS:
        mapping[name] = ("extension", "unsupported")
    return mapping


SUPPORT: dict[str, tuple[str, str]] = _build_support()

_CONTRACT_RELPATH = Path("contracts") / "dbc-2.0.4.json"
_CONTRACT_CANDIDATES: tuple[Path, ...] = (
    _CONTRACT_RELPATH,
    Path("src") / "nicegui_bootstrap_components" / "contracts" / "dbc-2.0.4.json",
)
_CONTRACT_UNAVAILABLE = "contract data unavailable at this build"
_DIRECTIVE_RE = re.compile(r"\{\{([^{}]+)\}\}")
_KNOWN_DIRECTIVES = frozenset({"apidoc", "code-example", "example"})


def _library_and_dbc_names(prop_name: str) -> tuple[str, str]:
    """Return ``(library_name, dbc_name)`` for a contract prop name."""
    partner = RENAMES.get(prop_name)
    if partner is None:
        return prop_name, prop_name
    if prop_name in _LIBRARY_TO_DBC:
        return prop_name, partner
    return partner, prop_name


def _support_pair(*names: str) -> tuple[str, str]:
    for name in names:
        pair = SUPPORT.get(name)
        if pair is not None:
            return pair
    return ("supported", "supported")


def _format_cell(value: object) -> str:
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    text = json.dumps(value) if isinstance(value, dict | list) else str(value)
    return text.replace("|", "\\|").replace("\r\n", " ").replace("\n", " ")


def _prop_type(prop: dict[str, Any]) -> object:
    for key in ("type_raw", "dbc_type"):
        if key in prop and prop[key] is not None:
            return prop[key]
    return ""


def _iter_props(entry: dict[str, Any]) -> list[dict[str, Any]]:
    raw = entry.get("props", [])
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def render_apidoc_table(
    component: str,
    contract: dict[str, Any],
    *,
    package_root: str | None = None,
) -> str:
    """Return a Markdown property table for ``component``.

    ``package_root`` is accepted for callers that resolve extra package metadata;
    rows are taken from ``contract`` only, in contract JSON order.
    """
    del package_root
    components = contract.get("components")
    if not isinstance(components, dict) or component not in components:
        raise ValueError(f"unknown component: {component}")
    entry = components[component]
    if not isinstance(entry, dict):
        raise ValueError(f"unknown component: {component}")

    lines = [
        "| " + " | ".join(PROPERTY_COLUMNS) + " |",
        "| " + " | ".join("---" for _ in PROPERTY_COLUMNS) + " |",
    ]
    for prop in _iter_props(entry):
        raw_name = str(prop.get("name", ""))
        library_name, dbc_name = _library_and_dbc_names(raw_name)
        native, compat = _support_pair(raw_name, library_name, dbc_name)
        cells = [
            _format_cell(library_name),
            _format_cell(_prop_type(prop)),
            _format_cell(prop.get("default")),
            _format_cell(dbc_name),
            _format_cell(native),
            _format_cell(compat),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _fence_python(source: str) -> str:
    body = source.replace("\r\n", "\n")
    if not body.endswith("\n"):
        body += "\n"
    return f"```python\n{body}```"


def render_code_example(rel_path: str, *, repo_root: str) -> str:
    """Return a fenced Python block with the full contents of ``rel_path``."""
    path = Path(repo_root) / rel_path
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return _fence_python(path.read_text(encoding="utf-8"))


def render_example_demo(rel_path: str, func: str = "demo", *, repo_root: str) -> str:
    """Return a fenced Python block with only ``func`` from ``rel_path``."""
    path = Path(repo_root) / rel_path
    if not path.is_file():
        raise FileNotFoundError(str(path))
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == func:
            end = node.end_lineno
            if end is None:
                raise ValueError(f"function {func!r} has no end line in {rel_path}")
            snippet = "".join(lines[node.lineno - 1 : end])
            return _fence_python(snippet)
    raise ValueError(f"function {func!r} not found in {rel_path}")


def _replace_one(
    raw: str,
    inner: str,
    *,
    repo_root: str,
    contract: dict[str, Any] | None,
    example_ids: dict[str, str] | None = None,
    image_prefix: str = "",
) -> str:
    parts = [part.strip() for part in inner.split(":")]
    kind = parts[0] if parts else ""
    if kind not in _KNOWN_DIRECTIVES:
        raise ValueError(f"unknown directive: {raw}")
    if kind == "apidoc":
        if len(parts) != 2 or not parts[1]:
            raise ValueError(f"malformed directive: {raw}")
        components = None if contract is None else contract.get("components")
        if not isinstance(components, dict) or not components:
            return _CONTRACT_UNAVAILABLE
        return render_apidoc_table(parts[1], contract or {})
    if kind == "code-example":
        if len(parts) != 2 or not parts[1]:
            raise ValueError(f"malformed directive: {raw}")
        return render_code_example(parts[1], repo_root=repo_root)
    if len(parts) != 3 or not parts[1] or not parts[2]:
        raise ValueError(f"malformed directive: {raw}")
    block = render_example_demo(parts[1], parts[2], repo_root=repo_root)
    preview = _example_preview(
        parts[1],
        repo_root=repo_root,
        example_ids=example_ids or {},
        image_prefix=image_prefix,
    )
    return preview + block


def _load_example_ids(repo_root: str) -> dict[str, str]:
    """Map example source paths to manifest ids (for preview screenshots)."""
    path = Path(repo_root) / "examples" / "manifest.yaml"
    if not path.is_file():
        return {}
    import yaml

    raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("examples", [])
    if not isinstance(raw, list):
        return {}
    mapping: dict[str, str] = {}
    for item in raw:
        if isinstance(item, dict) and item.get("id") and item.get("source"):
            mapping[str(item["source"])] = str(item["id"])
    return mapping


def _example_preview(
    rel_path: str,
    *,
    repo_root: str,
    example_ids: dict[str, str],
    image_prefix: str,
) -> str:
    """Return a markdown image for ``rel_path``'s captured preview, or ``''``."""
    example_id = example_ids.get(rel_path)
    if not example_id:
        return ""
    shot = Path(repo_root) / "docs_site" / "assets" / "examples" / f"{example_id}.png"
    if not shot.is_file():
        return ""
    return f"![{example_id} example]({image_prefix}assets/examples/{example_id}.png)\n\n"


def _page_image_prefix(page: object | None) -> str:
    """Relative path from a page's source file to the docs directory root."""
    file = getattr(page, "file", None)
    src_uri = str(getattr(file, "src_uri", "") or "") if file is not None else ""
    parts = Path(src_uri).parts if src_uri else ()
    if not parts:
        return ""
    # ``a/b/page.md`` sits one directory below ``a/``: climb ``len(parts) - 1``
    # levels to reach the docs root regardless of the file's name.
    return "../" * (len(parts) - 1)


def expand_directives(
    markdown: str,
    *,
    repo_root: str,
    contract: dict[str, Any] | None,
    image_prefix: str = "",
) -> str:
    """Replace ``{{apidoc:}}``, ``{{code-example:}}``, and ``{{example:}}`` directives."""

    example_ids = _load_example_ids(repo_root)

    def _sub(match: re.Match[str]) -> str:
        raw = match.group(0)
        inner = match.group(1).strip()
        if not inner:
            raise ValueError(f"malformed directive: {raw}")
        return _replace_one(
            raw,
            inner,
            repo_root=repo_root,
            contract=contract,
            example_ids=example_ids,
            image_prefix=image_prefix,
        )

    return _DIRECTIVE_RE.sub(_sub, markdown)


def _config_file_parent(config: object | None) -> Path:
    path: object | None = None
    if config is None:
        return Path.cwd()
    if isinstance(config, dict):
        path = config.get("config_file_path")
    else:
        path = getattr(config, "config_file_path", None)
        if path is None:
            getter = getattr(config, "get", None)
            if callable(getter):
                path = getter("config_file_path")
    if path is None or path == "":
        return Path.cwd()
    return Path(str(path)).expanduser().resolve().parent


def _read_contract(repo_root: Path) -> dict[str, Any]:
    for relpath in _CONTRACT_CANDIDATES:
        path = repo_root / relpath
        if not path.is_file():
            continue
        loaded: Any = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            return loaded
    return {}


def on_page_markdown(
    markdown: str,
    *,
    page: object | None = None,
    config: object | None = None,
    files: object | None = None,
    **kwargs: Any,
) -> str:
    """Expand documentation directives in a MkDocs page."""
    del files, kwargs
    repo_root = _config_file_parent(config)
    contract = _read_contract(repo_root)
    return expand_directives(
        markdown,
        repo_root=str(repo_root),
        contract=contract,
        image_prefix=_page_image_prefix(page),
    )
