"""Example manifest parsing and route helpers for the demo service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

__all__ = [
    "ExampleEntry",
    "dedupe",
    "load_manifest",
    "module_path_for",
    "route_for",
]

_REQUIRED_FIELDS = ("id", "title", "route", "source")


@dataclass
class ExampleEntry:
    """One example declared in the examples manifest."""

    id: str
    title: str
    route: str
    source: str
    components: list[str]
    extras: list[str]
    version: str


def route_for(entry_id: str) -> str:
    """Return the demo URL path for an example id."""
    return f"/examples/{entry_id}/"


def module_path_for(entry: ExampleEntry) -> str:
    """Convert an example source path to a dotted module path."""
    normalized = entry.source.replace("\\", "/").strip()
    parts = Path(normalized).with_suffix("").parts
    return ".".join(part for part in parts if part not in {"", "."})


def dedupe(entries: list[ExampleEntry]) -> list[ExampleEntry]:
    """Return entries with unique ids.

    Later entries with the same id replace earlier ones. Remaining order
    follows the first occurrence of each id.
    """
    by_id: dict[str, ExampleEntry] = {}
    order: list[str] = []
    for entry in entries:
        if entry.id not in by_id:
            order.append(entry.id)
        by_id[entry.id] = entry
    return [by_id[entry_id] for entry_id in order]


def load_manifest(path: str | Path) -> list[ExampleEntry]:
    """Parse ``path`` as an examples YAML manifest.

    A missing file yields an empty list. Entries missing ``id``, ``title``,
    ``route``, or ``source`` raise ``ValueError`` naming the offending entry.
    """
    manifest_path = Path(path)
    if not manifest_path.is_file():
        return []
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if raw is None:
        return []
    return [_parse_entry(item, index) for index, item in enumerate(_manifest_items(raw))]


def _manifest_items(raw: object) -> list[Any]:
    if isinstance(raw, list):
        return list(raw)
    if isinstance(raw, dict):
        if "examples" not in raw:
            return []
        examples = raw["examples"]
        if examples is None:
            return []
        if not isinstance(examples, list):
            raise ValueError("manifest examples must be a list")
        return list(examples)
    raise ValueError("manifest must be a list or a mapping with an examples key")


def _parse_entry(item: object, index: int) -> ExampleEntry:
    if not isinstance(item, dict):
        raise ValueError(f"malformed example entry at index {index}")
    entry_id = item.get("id")
    label = str(entry_id) if _has_value(entry_id) else f"at index {index}"
    missing = [field for field in _REQUIRED_FIELDS if not _has_value(item.get(field))]
    if missing:
        raise ValueError(f"malformed example entry {label}: missing {', '.join(missing)}")
    version = item.get("version", "")
    if version is None:
        version = ""
    return ExampleEntry(
        id=str(item["id"]),
        title=str(item["title"]),
        route=str(item["route"]),
        source=str(item["source"]),
        components=_string_list(item.get("components"), "components", label),
        extras=_string_list(item.get("extras"), "extras", label),
        version=str(version),
    )


def _has_value(value: object) -> bool:
    return value is not None and value != ""


def _string_list(value: object, field: str, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"malformed example entry {label}: {field} must be a list")
    return [str(part) for part in value]
