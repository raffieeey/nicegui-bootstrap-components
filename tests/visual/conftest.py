"""Fixtures and CLI options for the visual accessibility matrix."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from collections.abc import Iterator
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from PIL import Image, ImageChops

if TYPE_CHECKING:
    from playwright.sync_api import Page

BASELINES_DIR = Path(__file__).resolve().parent / "baselines"
AXE_CORE_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEMO_SCRIPT = "scripts/prototype_demo.py"

# Glyph rasterization differs between machines and browser builds, so screenshots
# are compared with a small tolerance: the average pixel delta and the share of
# notably different pixels must all stay below these limits.
MEAN_DELTA_LIMIT = 10.0
SOFT_DELTA = 32
SOFT_FRACTION_LIMIT = 8.0
STRONG_DELTA = 128
STRONG_FRACTION_LIMIT = 6.0


def compare_pngs(expected: bytes, actual: bytes) -> tuple[bool, str]:
    """Compare two PNG byte strings; return ``(matches, summary)``.

    Byte-identical images match immediately. Differing canvas sizes never match.
    Otherwise the images match when all three limits hold: average pixel delta
    below ``MEAN_DELTA_LIMIT``, the share of pixels above ``SOFT_DELTA`` below
    ``SOFT_FRACTION_LIMIT``, and the share above ``STRONG_DELTA`` below
    ``STRONG_FRACTION_LIMIT``. The summary reports the measured values.
    """
    if expected == actual:
        return True, "identical"
    a = Image.open(BytesIO(expected))
    b = Image.open(BytesIO(actual))
    if a.size != b.size:
        return False, f"size mismatch: {a.size} vs {b.size}"
    delta = ImageChops.difference(a, b).convert("L")
    histogram = delta.histogram()
    total = delta.size[0] * delta.size[1]
    mean = sum(value * count for value, count in enumerate(histogram)) / total
    soft_pct = 100.0 * sum(histogram[SOFT_DELTA + 1 :]) / total
    strong_pct = 100.0 * sum(histogram[STRONG_DELTA + 1 :]) / total
    summary = f"mean_delta={mean:.2f} soft={soft_pct:.2f}% strong={strong_pct:.2f}%"
    matches = (
        mean < MEAN_DELTA_LIMIT
        and soft_pct < SOFT_FRACTION_LIMIT
        and strong_pct < STRONG_FRACTION_LIMIT
    )
    return matches, summary


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--visual",
        action="store_true",
        default=False,
        help="run visual regression and accessibility matrix tests",
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "visual: visual regression and axe-core checks; run with --visual",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if config.getoption("--visual"):
        return
    skip_visual = pytest.mark.skip(
        reason="visual tests are deselected unless --visual is passed",
    )
    for item in items:
        if item.get_closest_marker("visual") is not None:
            item.add_marker(skip_visual)


class VisualClient:
    """Helper for screenshot baselines and axe-core checks."""

    def __init__(self, page: Page, base_url: str, baselines_dir: Path) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self._baselines_dir = baselines_dir

    def _absolute_url(self, url_path: str) -> str:
        if url_path.startswith(("http://", "https://")):
            return url_path
        path = url_path if url_path.startswith("/") else f"/{url_path}"
        return f"{self.base_url}{path}"

    _THEME_SELECTOR = ".ngbs, .ngbs-overlay"
    _SETTLE_TIMEOUT_MS = 10_000

    def _wait_for_island(self, url_path: str) -> None:
        """Wait until at least one themed island element is mounted."""
        try:
            self.page.wait_for_function(
                f"() => document.querySelectorAll({json.dumps(self._THEME_SELECTOR)}).length > 0",
                timeout=self._SETTLE_TIMEOUT_MS,
            )
        except Exception as extra:  # noqa: BLE001
            raise AssertionError(f"no themed island mounted on {url_path}: {extra}") from extra

    def _wait_for_theme(self, url_path: str, expect_theme: str) -> None:
        """Wait until every island element carries the expected ``data-bs-theme``."""
        try:
            self.page.wait_for_function(
                "(want) => {"
                f" const els = document.querySelectorAll({json.dumps(self._THEME_SELECTOR)});"
                " if (els.length === 0) return false;"
                " return Array.from(els).every((el) => el.getAttribute('data-bs-theme') === want);"
                "}",
                arg=expect_theme,
                timeout=self._SETTLE_TIMEOUT_MS,
            )
        except Exception as extra:  # noqa: BLE001
            raise AssertionError(
                f"theme {expect_theme!r} was never applied on {url_path}: {extra}"
            ) from extra

    def screenshot(self, url_path: str, name: str, *, expect_theme: str | None = None) -> None:
        """Capture ``url_path`` after the page has settled, then compare to the baseline."""
        self.page.goto(self._absolute_url(url_path))
        self.page.evaluate("() => document.fonts.ready.then(() => true)")
        if expect_theme is not None:
            self._wait_for_theme(url_path, expect_theme)
        else:
            self._wait_for_island(url_path)
        # Two animation frames so the settled styles have actually painted.
        self.page.evaluate(
            "() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))"
        )
        png_bytes: bytes = self.page.screenshot()
        self._baselines_dir.mkdir(parents=True, exist_ok=True)
        baseline_path = self._baselines_dir / f"{name}.png"
        actual_path = self._baselines_dir / f"{name}.actual.png"
        if not baseline_path.is_file():
            baseline_path.write_bytes(png_bytes)
            pytest.skip("baseline created, re-run to compare")
        expected = baseline_path.read_bytes()
        if png_bytes == expected:
            if actual_path.is_file():
                actual_path.unlink()
            return
        ok, summary = compare_pngs(expected, png_bytes)
        if not ok:
            actual_path.write_bytes(png_bytes)
            raise AssertionError(
                f"screenshot mismatch: baseline={baseline_path} actual={actual_path} ({summary})"
            )
        if actual_path.is_file():
            actual_path.unlink()

    def assert_no_axe_violations(self, page: Page) -> dict[str, Any]:
        """Inject axe-core, fail on critical/serious impacts, return the report."""
        page.add_script_tag(url=AXE_CORE_URL)
        report = page.evaluate("() => axe.run()")
        if not isinstance(report, dict):
            raise AssertionError(f"axe.run() did not return a dict: {type(report)!r}")
        violations = report.get("violations", [])
        blocking = [item for item in violations if item.get("impact") in {"critical", "serious"}]
        if blocking:
            labels = ", ".join(str(item.get("id", "unknown")) for item in blocking)
            raise AssertionError(f"axe-core critical/serious violations: {labels}")
        return report


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _stop_process(proc: subprocess.Popen[bytes] | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=4)


def _spawn_visual_demo() -> tuple[subprocess.Popen[bytes], str]:
    demo_path = REPO_ROOT / DEMO_SCRIPT
    if not demo_path.is_file():
        raise FileNotFoundError(f"demo app missing: {demo_path}")
    port = _free_port()
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    for marker in ("PYTEST_CURRENT_TEST", "NICEGUI_SCREEN_TEST_PORT"):
        env.pop(marker, None)
    pythonpath = [str(REPO_ROOT)]
    src = REPO_ROOT / "src"
    if src.is_dir():
        pythonpath.append(str(src))
    existing = env.get("PYTHONPATH", "")
    if existing:
        pythonpath.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    proc = subprocess.Popen(
        [
            sys.executable,
            DEMO_SCRIPT,
            "--mode",
            "mixed",
            "--port",
            str(port),
        ],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
    )
    lines: deque[bytes] = deque(maxlen=200)

    def _drain() -> None:
        stream = proc.stdout
        if stream is None:
            return
        for raw in iter(stream.readline, b""):
            lines.append(raw)

    threading.Thread(target=_drain, daemon=True).start()
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 30
    last_error: Exception | None = None
    while time.time() < deadline:
        if proc.poll() is not None:
            tail = b"".join(lines).decode("utf-8", "replace")
            raise RuntimeError(f"prototype_demo exited {proc.returncode}: {tail}")
        try:
            with urllib.request.urlopen(url + "/", timeout=1) as response:
                if response.status == 200:
                    return proc, url
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as extra:
            last_error = extra
        time.sleep(0.15)
    tail = b"".join(lines).decode("utf-8", "replace")
    _stop_process(proc)
    raise TimeoutError(f"prototype_demo at {url} did not become ready: {last_error}\n{tail}")


@pytest.fixture(scope="session")
def visual_server() -> Iterator[str]:
    """Yield the mixed-mode demo URL, spawning it when no external base URL is set."""
    env_url = os.getenv("NGBC_VISUAL_BASE_URL")
    if env_url:
        yield env_url.rstrip("/")
        return
    proc: subprocess.Popen[bytes] | None = None
    try:
        proc, url = _spawn_visual_demo()
        yield url
    finally:
        _stop_process(proc)


@pytest.fixture(scope="session")
def visual_client(visual_server: str) -> Iterator[VisualClient]:
    """Yield a session-scoped Chromium helper for matrix tests."""
    from playwright.sync_api import sync_playwright

    base_url = os.getenv("NGBC_VISUAL_BASE_URL", visual_server)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            yield VisualClient(page=page, base_url=base_url, baselines_dir=BASELINES_DIR)
        finally:
            browser.close()
