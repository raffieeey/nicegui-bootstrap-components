"""Smoke tests that import every shipped example and execute its demo()."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"


def _example_files() -> list[Path]:
    return sorted(p for p in EXAMPLES_DIR.rglob("*.py") if "__pycache__" not in p.parts)


@pytest.mark.parametrize(
    "path",
    _example_files(),
    ids=lambda p: p.relative_to(REPO_ROOT).as_posix(),
)
def test_example_demo_runs(path: Path, nicegui_reset_globals) -> None:
    # Demos build elements at call time; NiceGUI only creates its implicit
    # script client when the global state is pristine, so reset it per test.
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    module_name = "nbc_example_" + "__".join(path.relative_to(REPO_ROOT).with_suffix("").parts)
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    if not hasattr(module, "demo"):
        # Page-function templates (multi-page examples) define ``page_*``
        # functions instead of a ``demo()``. Execute each zero-argument page
        # function so the example's element tree is actually built and any
        # runtime error (bad kwargs, broken adoption) fails the test.
        import inspect

        pages = [
            fn
            for name, fn in sorted(vars(module).items())
            if name.startswith("page_")
            and callable(fn)
            and not inspect.isclass(fn)
            and _accepts_no_required_args(fn)
        ]
        if not pages:
            pytest.skip("no demo()")
        for fn in pages:
            fn()
        return
    module.demo()


def _accepts_no_required_args(fn: object) -> bool:
    """True when ``fn`` can be called with no arguments."""
    import inspect

    try:
        signature = inspect.signature(fn)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    for parameter in signature.parameters.values():
        if (
            parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD)
            and parameter.default is parameter.empty
        ):
            return False
        if parameter.kind is parameter.KEYWORD_ONLY and parameter.default is parameter.empty:
            return False
    return True
