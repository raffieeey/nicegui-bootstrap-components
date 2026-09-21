"""L4 tests for the visual and accessibility matrix."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import pytest

CONFTEST_PATH = Path(__file__).resolve().parent / "conftest.py"
BASELINES_DIR = Path(__file__).resolve().parent / "baselines"

ROUTE_MODE_A = "/mode-a"
ROUTE_MODE_B = "/mode-b"
ROUTE_LIGHT = "/light"
ROUTE_DARK = "/dark"
ROUTES: tuple[str, ...] = (ROUTE_MODE_A, ROUTE_MODE_B, ROUTE_LIGHT, ROUTE_DARK)

ROUTE_THEMES: dict[str, str | None] = {
    ROUTE_MODE_A: None,
    ROUTE_MODE_B: None,
    ROUTE_LIGHT: "light",
    ROUTE_DARK: "dark",
}

VIEWPORT_SM = ("sm", 576, 800)
VIEWPORT_MD = ("md", 768, 900)
VIEWPORT_LG = ("lg", 1280, 900)
VIEWPORTS: tuple[tuple[str, int, int], ...] = (VIEWPORT_SM, VIEWPORT_MD, VIEWPORT_LG)


@pytest.mark.visual
@pytest.mark.parametrize(("breakpoint", "width", "height"), VIEWPORTS)
@pytest.mark.parametrize("route", ROUTES)
def test_visual_matrix(
    visual_client: Any,
    route: str,
    breakpoint: str,
    width: int,
    height: int,
) -> None:
    visual_client.page.set_viewport_size({"width": width, "height": height})
    slug = route.strip("/").replace("/", "-")
    # Color mode is applied client-side after navigation; waiting for it keeps
    # the capture deterministic instead of racing the theme script.
    visual_client.screenshot(route, f"{slug}-{breakpoint}", expect_theme=ROUTE_THEMES[route])


@pytest.mark.visual
def test_axe_helper_returns_violations_key(visual_client: Any) -> None:
    page = visual_client.page
    page.goto(f"{visual_client.base_url}/")
    report = visual_client.assert_no_axe_violations(page)
    assert isinstance(report, dict)
    assert "violations" in report


def test_visual_infrastructure_present(pytestconfig: pytest.Config) -> None:
    assert CONFTEST_PATH.is_file(), f"missing visual conftest helper: {CONFTEST_PATH}"
    visual_flag = pytestconfig.getoption("--visual")
    assert isinstance(visual_flag, bool)
    resolved = BASELINES_DIR.resolve()
    assert resolved.name == "baselines"


def _visual_conftest() -> Any:
    """Load the sibling conftest module by path, avoiding name ambiguity."""
    path = Path(__file__).resolve().parent / "conftest.py"
    spec = importlib.util.spec_from_file_location("visual_conftest_tolerance", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_compare_pngs_tolerance(tmp_path: Path) -> None:
    """Noise-only differences pass; structural and colour regressions fail."""
    import io

    from PIL import Image

    compare_pngs = _visual_conftest().compare_pngs

    def png(image: Image.Image) -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    base = Image.new("RGB", (200, 120), (240, 240, 240))

    ok, _ = compare_pngs(png(base), png(base))
    assert ok

    noisy = base.copy()
    pixels = noisy.load()
    for x in range(0, 200, 7):
        for y in range(0, 120, 7):
            pixels[x, y] = (232, 232, 232)
    ok, summary = compare_pngs(png(base), png(noisy))
    assert ok, summary

    regressed = base.copy()
    for x in range(20, 120):
        for y in range(20, 80):
            regressed.putpixel((x, y), (10, 10, 200))
    ok, summary = compare_pngs(png(base), png(regressed))
    assert not ok, summary

    ok, summary = compare_pngs(png(base), png(Image.new("RGB", (201, 120), (240, 240, 240))))
    assert not ok
    assert "size" in summary
