#!/usr/bin/env python3
"""Extract the dash-bootstrap-components 2.0.4 public component contract to JSON.

Run from the repository root with dash-bootstrap-components==2.0.4 (and dash)
installed. Writes contracts/dbc-2.0.4.json and the tracked package copy at
src/nicegui_bootstrap_components/contracts/dbc-2.0.4.json.
"""

from __future__ import annotations

import ast
import importlib.metadata
import inspect
import json
import re
import shutil
import sys
import textwrap
from pathlib import Path
from typing import Any

EXPECTED_DBC_VERSION = "2.0.4"
EXPECTED_COUNT = 66
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "contracts" / "dbc-2.0.4.json"
PACKAGE_CONTRACT_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "nicegui_bootstrap_components"
    / "contracts"
    / "dbc-2.0.4.json"
)

try:
    from dash.development.base_component import Component
except ImportError as exc:
    raise SystemExit(
        "error: the dash package is required to extract the DBC contract "
        "(pip install dash dash-bootstrap-components==2.0.4)"
    ) from exc

try:
    import dash_bootstrap_components as dbc
except ImportError as exc:
    raise SystemExit(
        "error: dash-bootstrap-components "
        f"{EXPECTED_DBC_VERSION} is required "
        f"(pip install dash-bootstrap-components=={EXPECTED_DBC_VERSION})"
    ) from exc

KNOWN_MODULES: tuple[str, ...] = (
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
)

# Longest-first Pascal prefixes for DBC src/components layout (27 modules).
_MODULE_PREFIXES: tuple[tuple[str, str], ...] = tuple(
    sorted(
        (
            ("Accordion", "accordion"),
            ("Alert", "alert"),
            ("Badge", "badge"),
            ("Breadcrumb", "breadcrumb"),
            ("ButtonGroup", "buttongroup"),
            ("Button", "button"),
            ("Card", "card"),
            ("Carousel", "carousel"),
            ("Checkbox", "input"),
            ("Checklist", "input"),
            ("Collapse", "collapse"),
            ("Col", "layout"),
            ("Container", "layout"),
            ("DropdownMenu", "dropdownmenu"),
            ("Fade", "fade"),
            ("Form", "form"),
            ("InputGroupText", "input"),
            ("InputGroup", "input"),
            ("Input", "input"),
            ("Label", "form"),
            ("ListGroup", "listgroup"),
            ("Modal", "modal"),
            ("Navbar", "nav"),
            ("Nav", "nav"),
            ("Offcanvas", "offcanvas"),
            ("Pagination", "pagination"),
            ("Placeholder", "placeholder"),
            ("Popover", "popover"),
            ("Progress", "progress"),
            ("RadioButton", "input"),
            ("RadioItems", "input"),
            ("Row", "layout"),
            ("Select", "input"),
            ("Spinner", "spinner"),
            ("Stack", "layout"),
            ("Switch", "input"),
            ("Table", "table"),
            ("Tabs", "tabs"),
            ("Tab", "tabs"),
            ("Textarea", "input"),
            ("Toast", "toast"),
            ("Tooltip", "tooltip"),
        ),
        key=lambda item: (-len(item[0]), item[0]),
    )
)

_INPUT_COMPONENTS: frozenset[str] = frozenset(
    {
        "Checkbox",
        "Checklist",
        "Input",
        "InputGroup",
        "InputGroupText",
        "RadioButton",
        "RadioItems",
        "Select",
        "Switch",
        "Textarea",
    }
)

DASH_ONLY_PROPS = frozenset(
    {
        "loading_state",
        "persistence",
        "persisted_props",
        "persistence_type",
        "key",
    }
)

_MISSING = object()

_SECTION_RE = re.compile(
    r"^(?P<lead>.*?)(?:\n|^)(?P<header>[ \t]*(?:Keyword arguments|Props):)"
    r"[ \t]*\n(?P<body>.*)$",
    re.IGNORECASE | re.DOTALL,
)
_PROP_RE = re.compile(
    r"^(?P<indent> *)-\s+(?P<name>[A-Za-z_][A-Za-z0-9_-]*)\s+"
    r"\((?P<declared>.+?)\):(?P<rest>.*)$"
)
_DEFAULT_PIECE_RE = re.compile(r"^default\s*[:=]?\s*(.+)$", re.IGNORECASE)
_OPTIONAL_PARENS_RE = re.compile(
    r"^(.*?)(?:\s*\(\s*(optional|required)\s*\))$",
    re.IGNORECASE | re.DOTALL,
)
_ENUM_RE = re.compile(r"a value equal to:\s*(.*)$", re.IGNORECASE | re.DOTALL)
_ENUM_TOKEN_RE = re.compile(
    r"'((?:\\'|[^'])*)'|\"((?:\\\"|[^\"])*)\"|\b(True|False|None)\b|(-?\d+(?:\.\d+)?)"
)
_SIMPLE_TYPES = {
    "string": "string",
    "number": "number",
    "boolean": "boolean",
    "bool": "boolean",
    "object": "object",
    "dict": "object",
    "array": "array",
    "list": "array",
    "enum": "enum",
}
_DECLARED_SPLIT_KEYWORDS = frozenset(
    {
        "optional",
        "required",
        "a",
        "an",
        "dict",
        "string",
        "number",
        "boolean",
        "default",
    }
)


def require_dbc_version() -> str:
    """Abort unless the installed dash-bootstrap-components version is 2.0.4."""
    meta: str | None
    try:
        meta = importlib.metadata.version("dash-bootstrap-components")
    except importlib.metadata.PackageNotFoundError:
        meta = None
    attr = getattr(dbc, "__version__", None)
    attr_s = str(attr) if attr is not None else None
    found = meta or attr_s
    if found != EXPECTED_DBC_VERSION:
        raise SystemExit(
            "error: dash-bootstrap-components "
            f"{EXPECTED_DBC_VERSION} is required, found {found or 'unknown'}"
        )
    if meta and attr_s and meta != attr_s:
        raise SystemExit(
            f"error: version mismatch: importlib.metadata={meta!r} dbc.__version__={attr_s!r}"
        )
    return EXPECTED_DBC_VERSION


def public_components() -> list[tuple[str, type]]:
    """Return public Component subclasses exported from the DBC package root."""
    all_names = getattr(dbc, "__all__", None)
    if all_names:
        names = [n for n in all_names if isinstance(n, str)]
    else:
        names = [n for n in dir(dbc) if not n.startswith("_")]

    found: list[tuple[str, type]] = []
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        try:
            obj = getattr(dbc, name)
        except AttributeError:
            continue
        if not inspect.isclass(obj):
            continue
        try:
            if not issubclass(obj, Component) or obj is Component:
                continue
        except TypeError:
            continue
        module_name = getattr(obj, "__module__", "") or ""
        if not module_name.startswith("dash_bootstrap_components"):
            continue
        seen.add(name)
        found.append((name, obj))
    found.sort(key=lambda item: item[0])
    return found


def _is_pascal_prefix(name: str, prefix: str) -> bool:
    if name == prefix:
        return True
    if not name.startswith(prefix):
        return False
    rest = name[len(prefix) :]
    return bool(rest) and rest[0].isupper()


def infer_module(component_name: str) -> str | None:
    """Return the DBC source-layout module for a public component class name."""
    if component_name in _INPUT_COMPONENTS:
        return "input"
    for prefix, module in _MODULE_PREFIXES:
        if _is_pascal_prefix(component_name, prefix):
            return module
    lowered = component_name.lower()
    if lowered in KNOWN_MODULES:
        return lowered
    return None


def _parse_ast(source: str) -> ast.AST | None:
    for candidate in (source, textwrap.dedent(source)):
        try:
            return ast.parse(candidate)
        except SyntaxError:
            continue
    return None


def _self_attr_name(target: ast.expr) -> str | None:
    if (
        isinstance(target, ast.Attribute)
        and isinstance(target.value, ast.Name)
        and target.value.id == "self"
        and isinstance(target.attr, str)
    ):
        return target.attr
    return None


def _assignments_in_init(source: str) -> dict[str, Any]:
    tree = _parse_ast(source)
    if tree is None:
        return {}
    inits = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "__init__"
    ]
    if not inits and tree.body and isinstance(tree.body[0], ast.FunctionDef):
        inits = [tree.body[0]]
    found: dict[str, Any] = {}
    for init in inits:
        for node in ast.walk(init):
            value_node: ast.expr | None = None
            targets: list[ast.expr] = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
                value_node = node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = [node.target]
                value_node = node.value
            if value_node is None:
                continue
            for target in targets:
                attr = _self_attr_name(target)
                if not attr:
                    continue
                try:
                    found[attr] = ast.literal_eval(value_node)
                except (ValueError, TypeError):
                    continue
    return found


def _init_assignments(cls: type) -> dict[str, Any]:
    """Literal `self.<attr> = ...` assignments from the generated `__init__`."""
    merged: dict[str, Any] = {}
    targets: list[Any] = [cls]
    init = getattr(cls, "__init__", None)
    if init is not None:
        targets.append(inspect.unwrap(init))
    for target in targets:
        try:
            source = inspect.getsource(target)
        except (OSError, TypeError):
            continue
        merged.update(_assignments_in_init(source))
    return merged


def _attr(cls: type, generated: dict[str, Any], name: str) -> Any:
    """Read a dash-generated attribute from the class MRO or its `__init__` body."""
    own: Any = _MISSING
    for base in cls.__mro__:
        if name in vars(base):
            own = vars(base)[name]
            break
    if own is _MISSING:
        own = getattr(cls, name, _MISSING)
    init_val = generated.get(name, _MISSING)
    if own is _MISSING:
        return init_val
    if init_val is _MISSING:
        return own
    if own in ((), [], None) and init_val not in ((), [], None):
        return init_val
    return own


def _as_str_seq(value: Any) -> list[str]:
    if value is _MISSING or value is None:
        return []
    if isinstance(value, str):
        return [value]
    try:
        return [item for item in value if isinstance(item, str)]
    except TypeError:
        return []


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [_jsonable(item) for item in sorted(value, key=str)]
    raise TypeError(f"not JSON-serializable: {type(value).__name__}")


def _clean_desc_lines(lines: list[str]) -> str | None:
    """Trim the block edges; preserve relative indentation inside the block."""
    if not lines:
        return None
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    if start >= end:
        return None
    block = lines[start:end]
    indents = [len(line) - len(line.lstrip(" ")) for line in block if line.strip()]
    pad = min(indents) if indents else 0
    dedented = [line[pad:] if line.strip() else "" for line in block]
    cleaned = "\n".join(dedented)
    return cleaned if cleaned.strip() else None


def parse_enum_values(type_raw: str) -> list[str] | None:
    """Parse Dash `a value equal to: ...` enumerations into string tokens."""
    match = _ENUM_RE.search(type_raw)
    if not match:
        return None
    values: list[str] = []
    seen: set[str] = set()
    for single, double, const, num in _ENUM_TOKEN_RE.findall(match.group(1).strip()):
        token = single or double or const or num
        if token not in seen:
            seen.add(token)
            values.append(token)
    return values or None


def normalize_dbc_type(type_raw: str | None) -> str | None:
    """Map a Dash docstring / `_type_names` fragment onto a simple type name."""
    if not type_raw:
        return None
    stripped = type_raw.strip()
    lower = stripped.lower()
    if lower.startswith("a value equal to"):
        return "enum"
    if lower in _SIMPLE_TYPES:
        return _SIMPLE_TYPES[lower]
    if lower.startswith("a list of or a singular"):
        return stripped
    if lower.startswith(("list of", "list ", "array of", "array ")):
        return "array"
    if lower.startswith(("dict ", "dict with", "object ", "object with")):
        return "object"
    if lower.startswith("boolean"):
        return "boolean"
    if lower.startswith("string"):
        return "string"
    if lower.startswith("number"):
        return "number"
    return stripped


def _leading_keyword(segment: str) -> str:
    stripped = segment.lstrip()
    if not stripped:
        return ""
    token: list[str] = []
    for char in stripped:
        if char.isalpha():
            token.append(char)
        else:
            break
    return "".join(token).lower()


def _split_declared_segments(declared: str) -> list[str]:
    """Split on ';' that start a type keyword; ignore ';' inside quotes."""
    text = declared.strip()
    segments: list[str] = []
    buf: list[str] = []
    quote: str | None = None
    escape = False
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if quote is not None:
            buf.append(char)
            if escape:
                escape = False
            elif char == "\\" and quote in {"'", '"'}:
                escape = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            buf.append(char)
            index += 1
            continue
        if char == ";":
            rest = text[index + 1 :]
            if _leading_keyword(rest) in _DECLARED_SPLIT_KEYWORDS:
                piece = "".join(buf).strip()
                if piece:
                    segments.append(piece)
                buf = []
                index += 1
                continue
        buf.append(char)
        index += 1
    tail = "".join(buf).strip()
    if tail:
        segments.append(tail)
    return segments


def parse_declared_type(declared: str) -> dict[str, Any]:
    """Split a Dash prop type clause into type, default, enum, and required."""
    pieces = _split_declared_segments(declared)
    type_pieces: list[str] = []
    optional: bool | None = None
    required: bool | None = None
    default: str | None = None
    for piece in pieces:
        low = piece.lower()
        if low == "optional":
            optional = True
            required = False
            continue
        if low == "required":
            required = True
            optional = False
            continue
        default_match = _DEFAULT_PIECE_RE.match(piece)
        if default_match and default_match.group(1).strip():
            default = default_match.group(1).strip().rstrip(".")
            continue
        type_pieces.append(piece)
    type_raw = "; ".join(type_pieces).strip()
    parens = _OPTIONAL_PARENS_RE.match(type_raw)
    if parens:
        type_raw = parens.group(1).strip()
        if parens.group(2).lower() == "optional":
            optional = True
            required = False
        else:
            required = True
            optional = False
    enum_vals = parse_enum_values(type_raw) if type_raw else None
    dbc_type = "enum" if enum_vals else normalize_dbc_type(type_raw)
    return {
        "type_raw": type_raw or None,
        "dbc_type": dbc_type,
        "optional": optional,
        "required": required,
        "default": default,
        "enum": enum_vals,
    }


def _nest_props(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    top: dict[str, dict[str, Any]] = {}
    stack: list[tuple[int, dict[str, Any]]] = []
    for entry in entries:
        indent = int(entry.pop("indent"))
        name = str(entry["name"])
        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            top[name] = entry
        else:
            parent = stack[-1][1]
            shape = parent.setdefault("shape", {})
            shape[name] = entry
        stack.append((indent, entry))
    return top


def _parse_prop_body(body: str) -> dict[str, dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    desc_lines: list[str] = []

    def flush() -> None:
        nonlocal current, desc_lines
        if current is None:
            return
        current["description"] = _clean_desc_lines(desc_lines)
        entries.append(current)
        current = None
        desc_lines = []

    for raw in body.split("\n"):
        line = raw.expandtabs(4).rstrip()
        prop_match = _PROP_RE.match(line)
        if prop_match:
            flush()
            parsed = parse_declared_type(prop_match.group("declared"))
            rest = (prop_match.group("rest") or "").strip()
            current = {
                "name": prop_match.group("name"),
                "indent": len(prop_match.group("indent")),
                **parsed,
            }
            desc_lines = [rest] if rest else []
            continue
        if current is not None:
            desc_lines.append(line)
    flush()
    return _nest_props(entries)


def parse_docstring(doc: str | None) -> tuple[str | None, dict[str, dict[str, Any]]]:
    """Return (lead description, top-level props) parsed from a Dash docstring."""
    if not doc or not str(doc).strip():
        return None, {}
    cleaned = inspect.cleandoc(str(doc).replace("\r\n", "\n").replace("\r", "\n"))
    match = _SECTION_RE.search(cleaned)
    if not match:
        lead = cleaned.strip() or None
        return lead, {}
    lead = match.group("lead").strip() or None
    return lead, _parse_prop_body(match.group("body"))


def snake_to_camel(name: str) -> str:
    """Return the React camelCase alias for a Python snake_case prop name."""
    if "_" not in name or name.startswith(("aria-", "data-")):
        return name
    parts = name.split("_")
    if not parts[0]:
        return name
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:] if part)


def _signature_param_names(cls: type) -> list[str]:
    try:
        func = inspect.unwrap(cls.__init__)
        sig = inspect.signature(func)
    except (TypeError, ValueError):
        return []
    names: list[str] = []
    for pname, param in sig.parameters.items():
        if pname == "self":
            continue
        if param.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        names.append(pname)
    return names


def _type_to_dbc(value: Any) -> str | None:
    if value is None or value is _MISSING:
        return None
    if isinstance(value, str):
        return normalize_dbc_type(value) or value
    if isinstance(value, dict) and "type" in value:
        return _type_to_dbc(value["type"])
    return normalize_dbc_type(str(value))


def _type_by_prop(type_names_raw: Any, prop_names_raw: list[str]) -> dict[str, Any]:
    if isinstance(type_names_raw, dict):
        return {str(key): val for key, val in type_names_raw.items()}
    if (
        isinstance(type_names_raw, (list, tuple))
        and prop_names_raw
        and len(type_names_raw) == len(prop_names_raw)
    ):
        return dict(zip(prop_names_raw, type_names_raw, strict=False))
    return {}


def _disposition() -> dict[str, Any]:
    return {"compat": "match", "native": "match", "note": None}


def _coerce_dbc_type(dbc_type: Any, type_raw: Any = None, fallback: Any = None) -> str:
    if isinstance(dbc_type, str) and dbc_type.strip():
        return dbc_type
    if isinstance(type_raw, str) and type_raw.strip():
        return normalize_dbc_type(type_raw) or type_raw.strip()
    mapped = _type_to_dbc(fallback)
    if isinstance(mapped, str) and mapped.strip():
        return mapped
    return "unknown"


def _shape_to_records(shape: dict[str, Any]) -> dict[str, Any]:
    """Serialize nested docstring props with the same flags as top-level props."""
    out: dict[str, Any] = {}
    for key, entry in shape.items():
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name") or key)
        rec: dict[str, Any] = {
            "name": name,
            "dbc_type": _coerce_dbc_type(entry.get("dbc_type"), entry.get("type_raw")),
            "default": entry.get("default") or None,
            "required": bool(entry.get("required") is True),
            "description": entry.get("description"),
            "enum": entry.get("enum") or None,
            "dash_only": name in DASH_ONLY_PROPS,
            "disposition": _disposition(),
        }
        type_raw = entry.get("type_raw")
        if type_raw:
            rec["type_raw"] = type_raw
        nested = entry.get("shape")
        if nested:
            rec["shape"] = _shape_to_records(nested)
        out[str(key)] = rec
    return out


def _collect_prop_names(
    cls: type,
    generated: dict[str, Any],
    doc_props: dict[str, dict[str, Any]],
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()

    def extend(seq: Any) -> None:
        for item in _as_str_seq(seq):
            if not item or item in seen or item in {"self", "args", "kwargs"}:
                continue
            seen.add(item)
            ordered.append(item)

    extend(_attr(cls, generated, "_prop_names"))
    extend(_attr(cls, generated, "_available_props"))
    extend(_attr(cls, generated, "available_properties"))
    extend(_signature_param_names(cls))
    extend(doc_props.keys())
    return ordered


def extract_component(name: str, cls: type) -> dict[str, Any]:
    """Build the contract record for a single public DBC component class."""
    generated = _init_assignments(cls)
    raw_doc = getattr(cls, "__doc__", None)
    docstring = None
    if raw_doc and str(raw_doc).strip():
        docstring = inspect.cleandoc(str(raw_doc).replace("\r\n", "\n").replace("\r", "\n"))
    description, doc_props = parse_docstring(docstring)

    prop_names_raw = _as_str_seq(_attr(cls, generated, "_prop_names"))
    required_attr = _attr(cls, generated, "_required_props")
    available_attr = _attr(cls, generated, "_available_props")
    type_names_attr = _attr(cls, generated, "_type_names")
    defaults_attr = _attr(cls, generated, "_defaults")
    required_names = set(_as_str_seq(required_attr))
    type_by_prop = _type_by_prop(
        type_names_attr if type_names_attr is not _MISSING else None,
        prop_names_raw,
    )
    ordered = _collect_prop_names(cls, generated, doc_props)

    aliases = {pname: snake_to_camel(pname) for pname in ordered if snake_to_camel(pname) != pname}

    props: list[dict[str, Any]] = []
    for pname in ordered:
        doc = doc_props.get(pname, {})
        is_required = pname in required_names
        if doc.get("required") is True:
            is_required = True
        if doc.get("optional") is True:
            is_required = False
        default = doc.get("default") or None
        record: dict[str, Any] = {
            "name": pname,
            "dbc_type": _coerce_dbc_type(
                doc.get("dbc_type"),
                doc.get("type_raw"),
                type_by_prop.get(pname),
            ),
            "default": default,
            "required": bool(is_required),
            "description": doc.get("description"),
            "enum": doc.get("enum") or None,
            "dash_only": pname in DASH_ONLY_PROPS,
            "disposition": _disposition(),
        }
        type_raw = doc.get("type_raw")
        if type_raw:
            record["type_raw"] = type_raw
        shape = doc.get("shape")
        if shape:
            record["shape"] = _jsonable(_shape_to_records(shape))
        props.append(record)

    component: dict[str, Any] = {
        "aliases": aliases,
        "dash_only_props": [p for p in ordered if p in DASH_ONLY_PROPS],
        "defaults": (_jsonable(defaults_attr) if defaults_attr is not _MISSING else None),
        "description": description if description is not None else "",
        "docstring": docstring if docstring is not None else "",
        "module": infer_module(name),
        "name": name,
        "prop_names": ordered,
        "props": props,
    }
    if required_attr is not _MISSING:
        component["required_props"] = _as_str_seq(required_attr)
    if available_attr is not _MISSING:
        component["available_props"] = _as_str_seq(available_attr)
    if type_names_attr is not _MISSING:
        component["type_names"] = _jsonable(type_names_attr)
    namespace = _attr(cls, generated, "_namespace")
    if namespace is not _MISSING and namespace is not None:
        component["namespace"] = str(namespace)
    react_type = _attr(cls, generated, "_type")
    if react_type is not _MISSING and react_type is not None:
        component["type"] = str(react_type)
    wildcards = _attr(cls, generated, "_valid_wildcard_attributes")
    if wildcards is not _MISSING:
        component["wildcard_attributes"] = _as_str_seq(wildcards)
    return component


def extract_contract() -> dict[str, Any]:
    """Build the contract mapping for the installed DBC 2.0.4 package."""
    version = require_dbc_version()
    classes = public_components()
    names = [name for name, _ in classes]
    if len(names) != EXPECTED_COUNT:
        raise SystemExit(
            f"error: expected {EXPECTED_COUNT} public component exports, "
            f"found {len(names)} ({', '.join(names)})"
        )
    components = {name: extract_component(name, cls) for name, cls in classes}
    uninferrable = [name for name, rec in components.items() if rec.get("module") is None]
    if uninferrable:
        print(
            "WARNING: cannot infer DBC module for: " + ", ".join(uninferrable),
            file=sys.stderr,
        )
    return {
        "dbc_version": version,
        "components": components,
        "count": len(components),
    }


def main() -> int:
    """Write the root artifact and the tracked package contract copy."""
    payload = extract_contract()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    OUTPUT_PATH.write_text(text, encoding="utf-8")
    PACKAGE_CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OUTPUT_PATH, PACKAGE_CONTRACT_PATH)
    print(f"Wrote {OUTPUT_PATH} and {PACKAGE_CONTRACT_PATH} ({payload['count']} components)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
