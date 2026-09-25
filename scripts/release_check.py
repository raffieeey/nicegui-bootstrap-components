"""Pre-release check battery for nicegui-bootstrap-components."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"
_TAIL_LINES = 40


def main(argv: list[str] | None = None) -> int:
    """Run the pre-release battery. Return 0 on success, 1 if any step failed."""
    parser = argparse.ArgumentParser(description="Run the pre-release check battery.")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip the wheel build and the wheel smoke test.",
    )
    parser.add_argument(
        "--skip-docs",
        action="store_true",
        help="Skip the mkdocs strict build.",
    )
    args = parser.parse_args(argv)

    tool_skip = None if _has_dev_extra(ROOT) else "[dev] extra is not declared in pyproject.toml"
    results: list[tuple[str, str]] = [
        ("ruff", _step_ruff(skip=tool_skip)),
        ("mypy", _run_check("mypy", [sys.executable, "-m", "mypy"], skip=tool_skip)),
        (
            "pytest",
            _run_check(
                "pytest",
                [sys.executable, "-m", "pytest", "-q"],
                skip=tool_skip,
            ),
        ),
    ]

    wheel_path: Path | None = None
    build_skipped = args.skip_build
    if args.skip_build:
        results.append(("wheel build", _report("wheel build", SKIP, "--skip-build")))
    else:
        build_status, wheel_path = _step_build()
        results.append(("wheel build", build_status))
        if build_status == SKIP:
            build_skipped = True

    results.append(("docs", _step_docs(skip=args.skip_docs)))
    results.append(
        ("wheel smoke", _step_smoke(wheel_path, build_skipped=build_skipped)),
    )
    return _summarize(results)


def _has_dev_extra(root: Path) -> bool:
    path = root / "pyproject.toml"
    if not path.is_file():
        return False
    if sys.version_info >= (3, 11):
        import tomllib

        with path.open("rb") as handle:
            data = tomllib.load(handle)
        project = data.get("project", {})
        if not isinstance(project, dict):
            return False
        extras = project.get("optional-dependencies", {})
        return isinstance(extras, dict) and "dev" in extras
    in_optional = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            in_optional = line == "[project.optional-dependencies]"
            continue
        if in_optional and (line.startswith("dev=") or line.startswith("dev =")):
            return True
    return False


def _run(
    argv: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd or ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            env=env,
        )
    except FileNotFoundError:
        return 127, f"command not found: {argv[0]}"
    output = completed.stdout or ""
    stderr = completed.stderr or ""
    if stderr:
        if output and not output.endswith("\n"):
            output += "\n"
        output += stderr
    return completed.returncode, output


def _print_tail(text: str, *, limit: int = _TAIL_LINES) -> None:
    lines = text.rstrip("\n").splitlines()
    if len(lines) > limit:
        lines = lines[-limit:]
    if lines:
        print("\n".join(lines))


def _report(title: str, status: str, detail: str = "", *, output: str = "") -> str:
    print(title)
    if detail:
        print(f"{status}  {detail}")
    else:
        print(status)
    if status == FAIL and output.strip():
        _print_tail(output)
    print()
    return status


def _run_check(title: str, argv: list[str], *, skip: str | None = None) -> str:
    if skip is not None:
        return _report(title, SKIP, skip)
    code, output = _run(argv)
    if code == 0:
        return _report(title, PASS)
    return _report(title, FAIL, output=output)


def _argv_or_module(program: str, module: str) -> list[str]:
    found = shutil.which(program)
    if found is not None:
        return [found]
    return [sys.executable, "-m", module]


def _step_ruff(*, skip: str | None) -> str:
    title = "ruff"
    if skip is not None:
        return _report(title, SKIP, skip)
    ruff = _argv_or_module("ruff", "ruff")
    check_code, check_out = _run([*ruff, "check", "."])
    # The formatter is scoped to Python sources: formatting prose pages would
    # rewrite authored documentation and is not part of the project's checks.
    fmt_code, fmt_out = _run([*ruff, "format", "--check", ".", "--exclude", "*.md"])
    if check_code == 0 and fmt_code == 0:
        return _report(title, PASS)
    output = "\n".join(part for part in (check_out, fmt_out) if part.strip())
    return _report(title, FAIL, output=output)


def _step_build() -> tuple[str, Path | None]:
    title = "wheel build"
    probe_code, _ = _run([sys.executable, "-c", "import build"])
    if probe_code != 0:
        return _report(title, SKIP, "build module is not installed"), None
    code, output = _run([sys.executable, "-m", "build", "--wheel"])
    if code != 0:
        return _report(title, FAIL, output=output), None
    wheel_path = _newest_wheel(ROOT / "dist")
    if wheel_path is None:
        return _report(title, FAIL, "no wheel produced in dist/"), None
    return _report(title, PASS), wheel_path


def _newest_wheel(dist: Path) -> Path | None:
    if not dist.is_dir():
        return None
    preferred = list(dist.glob("nicegui_bootstrap_components-*.whl"))
    candidates = preferred or list(dist.glob("*.whl"))
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _mkdocs_argv() -> list[str] | None:
    probe_code, _ = _run([sys.executable, "-c", "import mkdocs"])
    if probe_code == 0:
        return [sys.executable, "-m", "mkdocs"]
    found = shutil.which("mkdocs")
    if found is not None:
        return [found]
    return None


def _step_docs(*, skip: bool) -> str:
    title = "docs"
    if skip:
        return _report(title, SKIP, "--skip-docs")
    argv = _mkdocs_argv()
    if argv is None:
        return _report(title, SKIP, "mkdocs is not installed")
    return _run_check(title, [*argv, "build", "--strict"])


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _isolated_env() -> dict[str, str]:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _step_smoke(wheel_path: Path | None, *, build_skipped: bool) -> str:
    title = "wheel smoke"
    if wheel_path is None:
        reason = "wheel build was skipped" if build_skipped else "wheel is not available"
        return _report(title, SKIP, reason)
    env = _isolated_env()
    with tempfile.TemporaryDirectory(prefix="release-check-") as tmp:
        venv_dir = Path(tmp) / "venv"
        code, output = _run([sys.executable, "-m", "venv", str(venv_dir)], env=env)
        if code != 0:
            return _report(title, FAIL, "failed to create virtualenv", output=output)
        python = _venv_python(venv_dir)
        if not python.is_file():
            return _report(title, FAIL, f"venv python not found: {python}")
        wheel = str(wheel_path.resolve())
        code, output = _run([str(python), "-m", "pip", "install", wheel], env=env)
        if code != 0:
            return _report(
                title,
                FAIL,
                "pip install of the wheel failed",
                output=output,
            )
        code, output = _run([str(python), "-m", "pip", "install", "nicegui"], env=env)
        if code != 0:
            return _report(
                title,
                FAIL,
                "pip install of nicegui failed",
                output=output,
            )
        # Probe the documented top-level surface (README "Top-level exports").
        # `set_theme` is a ThemeController method, not a top-level export.
        probe = (
            "import nicegui_bootstrap_components as pkg\n"
            "expected = ('StyleMode', 'ThemeController', 'bs', 'dbc', 'icons', 'setup', 'themes')\n"
            "missing = [name for name in expected if not hasattr(pkg, name)]\n"
            "assert not missing, f'package does not expose: {missing}'\n"
            "assert pkg.__version__, 'package does not expose __version__'\n"
        )
        code, output = _run([str(python), "-c", probe], env=env)
        if code != 0:
            return _report(title, FAIL, "import smoke failed", output=output)
        return _report(title, PASS)


def _summarize(results: list[tuple[str, str]]) -> int:
    n_pass = sum(1 for _, status in results if status == PASS)
    n_fail = sum(1 for _, status in results if status == FAIL)
    n_skip = sum(1 for _, status in results if status == SKIP)
    print("Summary")
    name_width = max(len(name) for name, _status in results)
    for name, status in results:
        print(f"  {name:<{name_width}}  {status}")
    print()
    print(f"  passed: {n_pass}  failed: {n_fail}  skipped: {n_skip}")
    overall = PASS if n_fail == 0 else FAIL
    print(f"RELEASE CHECK: {overall}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
