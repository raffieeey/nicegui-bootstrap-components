"""CLI to list contract components, print API tables, and expand doc directives."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

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


def _hook() -> ModuleType:
    return importlib.import_module("docs_site._hooks.apidoc")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "List components, render API property tables, and expand documentation directives."
        ),
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True
    sub.add_parser("list", help="Print component names from the contract.")
    apidoc_p = sub.add_parser("apidoc", help="Print the property table for one component.")
    apidoc_p.add_argument("name", help="Component name, for example Button.")
    expand_p = sub.add_parser("expand", help="Expand directives in a Markdown file.")
    expand_p.add_argument("file", help="Markdown file containing directives.")
    expand_p.add_argument(
        "out",
        nargs="?",
        default=None,
        help="Optional output path. Defaults to stdout.",
    )
    return parser


def _load_contract(*, required: bool) -> dict[str, Any]:
    path = _resolve_contract()
    if path is None:
        if required:
            raise FileNotFoundError(
                f"contract not found; checked {PACKAGE_CONTRACT_PATH} and {ROOT_CONTRACT_PATH}"
            )
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        if required:
            raise ValueError(f"invalid contract: {path}")
        return {}
    return loaded


def _write_stdout(text: str) -> None:
    sys.stdout.write(text if text.endswith("\n") else f"{text}\n")


def _run(args: argparse.Namespace) -> int:
    hook = _hook()
    if args.command == "list":
        contract = _load_contract(required=True)
        components = contract.get("components")
        if not isinstance(components, dict):
            path = _resolve_contract()
            raise ValueError(f"invalid contract: {path}")
        for name in components:
            print(name)
        return 0
    if args.command == "apidoc":
        contract = _load_contract(required=True)
        _write_stdout(hook.render_apidoc_table(args.name, contract))
        return 0
    if args.command == "expand":
        path = Path(args.file)
        if not path.is_file():
            raise FileNotFoundError(f"markdown file not found: {path}")
        markdown = path.read_text(encoding="utf-8")
        expanded = hook.expand_directives(
            markdown,
            repo_root=str(_REPO_ROOT),
            contract=_load_contract(required=False),
        )
        if args.out:
            Path(args.out).write_text(expanded, encoding="utf-8")
        else:
            sys.stdout.write(expanded)
        return 0
    raise ValueError(f"unknown command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Expected errors print a short message and return 1."""
    args = _build_parser().parse_args(argv)
    try:
        return _run(args)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except ValueError as orig:
        print(str(orig), file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid contract JSON: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
