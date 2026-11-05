"""Real Chromium check for the dismissed alert's descendants."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def _serve(port: int) -> None:
    from nicegui import ui

    from nicegui_bootstrap_components import StyleMode, bs, setup

    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with bs.scope():
            with bs.Alert(dismissable=True, fade=True).classes("probe-alert") as alert:
                bs.Button("Focusable descendant").classes("probe-child")

            def reopen() -> None:
                alert.is_open = True

            ui.button("Reopen", on_click=reopen).classes("probe-reopen")

    ui.run(host="127.0.0.1", port=port, reload=False, show=False, reconnect_timeout=2)


@pytest.mark.browser
def test_f05_browser_hidden_descendants_and_reopen() -> None:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = os.environ.copy()
    env.pop("PYTEST_CURRENT_TEST", None)
    env.pop("NICEGUI_SCREEN_TEST_PORT", None)
    proc = subprocess.Popen(
        [sys.executable, __file__, str(port)],
        cwd=ROOT,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(200):
            if proc.poll() is not None:
                raise RuntimeError(f"loopback server exited {proc.returncode}")
            try:
                with urllib.request.urlopen(base, timeout=1):
                    break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(0.1)
        else:
            raise TimeoutError("loopback server failed to start")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context()
            external = []

            def block_external(route) -> None:
                if route.request.url.startswith(base + "/"):
                    route.continue_()
                else:
                    external.append(route.request.url)
                    route.abort()

            context.route("**/*", block_external)
            page = context.new_page()
            page.goto(base, wait_until="networkidle")
            alert = page.locator(".probe-alert")
            child = page.locator(".probe-child")
            alert.locator(".btn-close").click()
            alert.wait_for(state="hidden")
            assert alert.evaluate("(el) => getComputedStyle(el).display") == "none"
            child.evaluate("(el) => el.focus()")
            assert not child.evaluate("(el) => el === document.activeElement")
            assert not child.is_visible()
            page.locator(".probe-reopen").click()
            alert.wait_for(state="visible")
            assert child.is_visible()
            assert not external, external
            context.close()
            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=4)


if __name__ == "__main__":
    _serve(int(sys.argv[1]))
