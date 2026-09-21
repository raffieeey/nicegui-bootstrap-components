"""Pytest plugins and prototype-app fixtures for L3 Playwright tests."""

from __future__ import annotations

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
from dataclasses import dataclass
from pathlib import Path

import pytest

pytest_plugins = ["nicegui.testing.plugin"]

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "scripts" / "prototype_demo.py"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "browser: Playwright L3 browser tests")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _stop(proc: subprocess.Popen[bytes] | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=4)


def _spawn(mode: str) -> tuple[subprocess.Popen[bytes], str]:
    if not DEMO.is_file():
        raise FileNotFoundError(f"demo app missing: {DEMO}")
    port = _free_port()
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    # The demo runs its own NiceGUI server in a subprocess; pytest env markers
    # would make ui.run take the in-test branch (KeyError on the screen port).
    for marker in ("PYTEST_CURRENT_TEST", "NICEGUI_SCREEN_TEST_PORT"):
        env.pop(marker, None)
    pythonpath = [str(ROOT)]
    src = ROOT / "src"
    if src.is_dir():
        pythonpath.append(str(src))
    existing = env.get("PYTHONPATH", "")
    if existing:
        pythonpath.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    proc = subprocess.Popen(
        [
            sys.executable,
            str(DEMO),
            "--mode",
            mode,
            "--port",
            str(port),
            "--host",
            "127.0.0.1",
        ],
        cwd=str(ROOT),
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
    deadline = time.time() + 45
    last_error: Exception | None = None
    while time.time() < deadline:
        if proc.poll() is not None:
            tail = b"".join(lines).decode("utf-8", "replace")
            raise RuntimeError(f"prototype_demo ({mode}) exited {proc.returncode}: {tail}")
        try:
            with urllib.request.urlopen(url + "/", timeout=1) as response:
                if response.status < 500:
                    return proc, url
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            last_error = exc
        time.sleep(0.15)
    tail = b"".join(lines).decode("utf-8", "replace")
    _stop(proc)
    raise TimeoutError(
        f"prototype_demo ({mode}) at {url} did not become ready: {last_error}\n{tail}"
    )


@dataclass(frozen=True)
class Servers:
    mixed: str
    unscoped: str


@pytest.fixture(scope="session")
def servers() -> Iterator[Servers]:
    mixed_proc, mixed_url = _spawn("mixed")
    unscoped_proc: subprocess.Popen[bytes] | None = None
    try:
        unscoped_proc, unscoped_url = _spawn("unscoped")
        yield Servers(mixed=mixed_url, unscoped=unscoped_url)
    finally:
        _stop(mixed_proc)
        _stop(unscoped_proc)


@pytest.fixture(scope="session")
def server(servers: Servers) -> str:
    return servers.mixed


@pytest.fixture(scope="session")
def server_unscoped(servers: Servers) -> str:
    return servers.unscoped
