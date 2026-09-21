"""Execute every Python code block of every docs page and fail on any error.

Docs samples are public API surface: if a block cannot run against the shipped
library, the page teaches a broken call. Each block runs in a fresh process so
cross-block state (``setup()`` conflicts, slot state) cannot produce false
positives.

``{{example:...}}`` directives are expanded first (the same expansion MkDocs
applies at build time), so the suite executes exactly the code the site renders -
including every snippet pulled in from ``examples/``. Blocks that intentionally
demonstrate errors or call ``ui.run`` are skipped by an explicit allowlist;
everything else must execute cleanly.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs_site"
HOOKS_DIR = DOCS_DIR / "_hooks"

# Blocks whose demonstrated behaviour IS the point of the sample: a raised
# error, a deliberate duplicate ``setup()``, or a blocking ``ui.run``.
# Keyed by ``<relative path>::<block index>``; keep this list explicit so a
# new broken block cannot hide here silently.
ALLOWED_FAILURES: dict[str, str] = {}

_BLOCK_RE = re.compile(r"```python\n(.*?)```", re.S)

# ``ui.run()`` starts a blocking server and is a no-op under test; stub it so
# app-shaped samples (page + ui.run) still execute their component calls.
_PRELUDE = "import nicegui.ui as _ngui\n_ngui.run = lambda *a, **k: None\n"


def _docs_pages() -> list[Path]:
    return sorted(p for p in DOCS_DIR.rglob("*.md") if "site" not in p.parts)


def _expand_directives(markdown: str) -> str:
    """Expand ``{{example:}}`` / ``{{code-example:}}`` / ``{{apidoc:}}`` as MkDocs does."""
    spec = __import__("importlib.util", fromlist=["util"]).spec_from_file_location(
        "docs_apidoc_hook", HOOKS_DIR / "apidoc.py"
    )
    assert spec is not None and spec.loader is not None
    module = __import__("importlib.util", fromlist=["util"]).module_from_spec(spec)
    spec.loader.exec_module(module)
    contract = _load_contract(module)
    return module.expand_directives(str(markdown), repo_root=str(REPO_ROOT), contract=contract)


def _load_contract(module: object) -> dict:
    import json

    for relpath in (
        Path("contracts") / "dbc-2.0.4.json",
        Path("src") / "nicegui_bootstrap_components" / "contracts" / "dbc-2.0.4.json",
    ):
        path = REPO_ROOT / relpath
        if path.is_file():
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                return loaded
    return {}


def _blocks(text: str) -> list[str]:
    return _BLOCK_RE.findall(text)


def _run_block(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", _PRELUDE + code],
        capture_output=True,
        text=True,
        timeout=90,
        cwd=str(REPO_ROOT),
    )


@pytest.mark.parametrize("page", _docs_pages(), ids=lambda p: p.relative_to(REPO_ROOT).as_posix())
def test_docs_code_blocks_execute(page: Path) -> None:
    expanded = _expand_directives(page.read_text(encoding="utf-8"))
    blocks = _blocks(expanded)
    if not blocks:
        pytest.skip("no python blocks")
    failures: list[str] = []
    for index, block in enumerate(blocks, 1):
        if block.strip().startswith("!"):
            continue
        key = f"{page.relative_to(REPO_ROOT).as_posix()}::b{index}"
        if key in ALLOWED_FAILURES:
            continue
        result = _run_block(block)
        if result.returncode != 0:
            last_line = (result.stderr or "").strip().splitlines()
            detail = last_line[-1] if last_line else "no stderr"
            failures.append(f"{key}: {detail}")
    assert not failures, "docs code blocks failed:\n" + "\n".join(failures)
