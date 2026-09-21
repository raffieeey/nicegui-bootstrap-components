"""Playwright browser tests for the CSS and overlay behavior."""

from __future__ import annotations

import os
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest

pytest.importorskip("playwright")

from playwright.async_api import Page, async_playwright, expect

pytestmark = pytest.mark.browser

_PRIMARY = "rgb(13,110,253)"
_BODY_BG = "rgb(255,255,255)"
_BODY_FG = "rgb(33,37,41)"
_WAIT = 20_000


def _norm_color(value: str) -> str:
    compact = re.sub(r"\s+", "", value.strip().lower())
    match = re.fullmatch(r"rgba\((\d+),(\d+),(\d+),1(?:\.0+)?\)", compact)
    if match:
        return f"rgb({match.group(1)},{match.group(2)},{match.group(3)})"
    if compact in {"#0d6efd", "#0d6efdff"}:
        return _PRIMARY
    if compact in {"#fff", "#ffffff", "#ffffffff"}:
        return _BODY_BG
    if compact in {"#212529", "#212529ff"}:
        return _BODY_FG
    return compact


@asynccontextmanager
async def _chromium(
    viewport: dict[str, int] | None = None,
) -> AsyncIterator[Page]:
    async with async_playwright() as playwright:
        args = ["--no-sandbox"] if os.environ.get("CI") else []
        browser = await playwright.chromium.launch(args=args)
        context = await browser.new_context(
            viewport=viewport or {"width": 1024, "height": 800},
        )
        page = await context.new_page()
        page.set_default_timeout(_WAIT)
        try:
            yield page
        finally:
            await context.close()
            await browser.close()


async def _goto(page: Page, base: str, path: str, wait_for: str) -> None:
    await page.goto(f"{base}{path}", wait_until="domcontentloaded")
    await page.wait_for_selector(wait_for, timeout=_WAIT)


async def _css(page: Page, selector: str, js_prop: str) -> str:
    # Computed-style probes must also work on hidden elements (closed
    # collapse panels, dismissed overlays): attach, don't require visible.
    await page.wait_for_selector(selector, state="attached", timeout=_WAIT)
    value = await page.eval_on_selector(
        selector,
        f"el => getComputedStyle(el).{js_prop}",
    )
    return str(value)


async def _width(page: Page, selector: str) -> float:
    await page.wait_for_selector(selector, timeout=_WAIT)
    value = await page.eval_on_selector(
        selector,
        "el => el.getBoundingClientRect().width",
    )
    return float(value)


async def test_collapse_not_visibility_collapse(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#btn-toggle-collapse")
        await expect(page.locator("#collapse-panel, .probe-collapse")).to_have_count(1)
        await page.locator("#btn-toggle-collapse").click()
        await page.wait_for_function(
            """() => {
              const el = document.querySelector('#collapse-panel, .probe-collapse');
              if (!el) return false;
              const style = getComputedStyle(el);
              return style.visibility === 'visible' && style.display === 'block';
            }""",
            timeout=_WAIT,
        )
        visibility = await _css(page, "#collapse-panel, .probe-collapse", "visibility")
        display = await _css(page, "#collapse-panel, .probe-collapse", "display")
        assert visibility == "visible", visibility
        assert display == "block", display
        await page.locator("#btn-toggle-collapse").click()
        await page.wait_for_function(
            """() => {
              const el = document.querySelector('#collapse-panel, .probe-collapse');
              if (!el) return false;
              return getComputedStyle(el).display === 'none';
            }""",
            timeout=_WAIT,
        )
        hidden_display = await _css(page, "#collapse-panel, .probe-collapse", "display")
        hidden_visibility = await _css(
            page,
            "#collapse-panel, .probe-collapse",
            "visibility",
        )
        assert hidden_display == "none", hidden_display
        assert hidden_visibility == "visible", hidden_visibility


async def test_text_primary_mode_b(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#probe-text-primary")
        color = await _css(page, "#probe-text-primary", "color")
        assert _norm_color(color) == _PRIMARY, (
            f"Mode B text-primary was {color!r}; Bootstrap primary is rgb(13, 110, 253), "
            "Quasar primary is typically rgb(25, 118, 210)"
        )


async def test_text_primary_mode_a(server_unscoped: str) -> None:
    async with _chromium() as page:
        await _goto(page, server_unscoped, "/mode-a", "#probe-text-primary")
        color = await _css(page, "#probe-text-primary", "color")
        assert _norm_color(color) == _PRIMARY, (
            f"Mode A text-primary was {color!r}; expected Bootstrap rgb(13, 110, 253)"
        )


async def test_col_responsive(server: str) -> None:
    async with _chromium(viewport={"width": 900, "height": 720}) as page:
        await _goto(page, server, "/mode-b", "#probe-col")
        await page.wait_for_timeout(250)
        row_wide = await _width(page, "#probe-row")
        col_wide = await _width(page, "#probe-col")
        assert row_wide > 0
        assert col_wide / row_wide == pytest.approx(0.5, abs=0.12), (
            f"md=6 at 900px: col={col_wide} row={row_wide}"
        )
        await page.set_viewport_size({"width": 375, "height": 720})
        await page.wait_for_timeout(250)
        row_narrow = await _width(page, "#probe-row")
        col_narrow = await _width(page, "#probe-col")
        assert row_narrow > 0
        assert col_narrow / row_narrow == pytest.approx(1.0, abs=0.12), (
            f"xs=12 at 375px: col={col_narrow} row={row_narrow}"
        )


async def test_typography_in_scope(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", ".ngbs .btn")
        await page.wait_for_selector(".ngbs .form-control", timeout=_WAIT)
        btn_font = await _css(page, ".ngbs .btn", "fontFamily")
        input_font = await _css(page, ".ngbs .form-control", "fontFamily")
        for stack in (btn_font, input_font):
            lowered = stack.lower()
            assert "system-ui" in lowered, stack
            assert not lowered.strip().strip("\"'").startswith("roboto"), stack
        ngbs_bg = await _css(page, ".ngbs", "backgroundColor")
        ngbs_fg = await _css(page, ".ngbs", "color")
        assert _norm_color(ngbs_bg) == _BODY_BG, ngbs_bg
        assert _norm_color(ngbs_fg) == _BODY_FG, ngbs_fg


async def test_head_has_layer_overrides(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#mode-flag")
        styles = await page.locator("head style").all_text_contents()
        assert any("@layer overrides" in style for style in styles)


async def test_vue_import_resolves(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#mode-flag")
        info = await page.evaluate(
            """async () => {
              const mod = await import('vue');
              let resolved = '';
              const tag = document.querySelector('script[type="importmap"]');
              if (tag && tag.textContent) {
                try {
                  resolved = (JSON.parse(tag.textContent).imports || {}).vue || '';
                } catch (err) {
                  resolved = '';
                }
              }
              if (!resolved && performance) {
                const hit = performance.getEntriesByType('resource')
                  .map((entry) => entry.name)
                  .find((name) => name.includes('vue.esm-browser'));
                if (hit) resolved = hit;
              }
              const ctor = mod.createApp || mod.default;
              return {
                resolved,
                hasCreateApp: typeof mod.createApp === 'function',
                ctorType: typeof ctor,
                version: mod.version || (mod.default && mod.default.version) || '',
              };
            }"""
        )
        assert info["hasCreateApp"] or info["ctorType"] == "function", info
        assert "/_nicegui/" in info["resolved"], info
        assert "vue.esm-browser" in info["resolved"], info


async def test_modal_open_close_esc_delete_cleanup(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#btn-open-modal")
        await page.locator("#btn-open-modal").click()
        await expect(page.locator("#ngbs-overlay-root .modal.show")).to_be_visible(
            timeout=_WAIT,
        )
        contained = await page.evaluate(
            """() => {
              const root = document.getElementById('ngbs-overlay-root');
              const modal = document.querySelector('.modal');
              return !!(root && root.parentElement === document.body
                && modal && root.contains(modal));
            }"""
        )
        assert contained
        await page.keyboard.press("Escape")
        await page.wait_for_function(
            "() => !document.querySelector('#ngbs-overlay-root .modal.show')",
            timeout=_WAIT,
        )
        await page.locator("#btn-open-modal").click()
        await expect(page.locator("#ngbs-overlay-root .modal.show")).to_be_visible(
            timeout=_WAIT,
        )
        await page.keyboard.press("Escape")
        await page.wait_for_function(
            "() => !document.querySelector('#ngbs-overlay-root .modal.show')",
            timeout=_WAIT,
        )
        await page.locator("#btn-save").click()
        await expect(page.locator("#label-status")).to_have_text("Saved")
        await page.wait_for_function(
            "() => { const el = document.querySelector('.modal'); "
            "return el && !el.classList.contains('show') "
            "&& el.getAttribute('data-ngbs-open') === 'false'; }",
            timeout=_WAIT,
        )
        toggle = page.locator("#btn-toggle-modal")
        for expected_open in (True, False, True):
            await toggle.click(force=True)
            await page.wait_for_function(
                """(expected) => {
                  const modal = document.querySelector('#ngbs-overlay-root .modal');
                  if (!modal) return false;
                  const shown = modal.classList.contains('show');
                  const open = modal.getAttribute('data-ngbs-open') === 'true';
                  const backdrops = document.querySelectorAll('#ngbs-overlay-root .modal-backdrop').length;
                  return shown === expected && open === expected
                    && backdrops === (expected ? 1 : 0);
                }""",
                arg=expected_open,
                timeout=_WAIT,
            )
        shown = await page.locator("#ngbs-overlay-root .modal.show").count()
        backdrops = await page.locator("#ngbs-overlay-root .modal-backdrop").count()
        assert shown == 1
        assert backdrops == 1
        locked_while_inconsistent = await page.evaluate(
            """() => {
              const shown = document.querySelector('#ngbs-overlay-root .modal.show');
              const style = getComputedStyle(document.body);
              const locked = document.body.classList.contains('modal-open')
                || style.overflow === 'hidden'
                || style.overflowY === 'hidden';
              return !shown && locked;
            }"""
        )
        assert not locked_while_inconsistent
        if shown == 0:
            await page.locator("#btn-open-modal").click(force=True)
            await expect(page.locator("#ngbs-overlay-root .modal.show")).to_be_visible(
                timeout=_WAIT,
            )
        await page.locator("#btn-delete-modal").click(force=True)
        await page.wait_for_function(
            "() => document.querySelectorAll('.modal-backdrop').length === 0",
            timeout=_WAIT,
        )
        assert await page.locator(".modal-backdrop").count() == 0
        locked = await page.evaluate(
            """() => {
              const style = getComputedStyle(document.body);
              return document.body.classList.contains('modal-open')
                || style.overflow === 'hidden'
                || style.overflowY === 'hidden';
            }"""
        )
        assert locked is False


async def test_dropdown_outside_click_esc(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#probe-dropdown")
        dropdown = page.locator("#probe-dropdown")
        inner_button = page.locator("#probe-dropdown button")
        if await inner_button.count():
            await inner_button.first.click()
        else:
            await dropdown.click()
        await expect(page.locator(".dropdown-menu.show")).to_be_visible(timeout=_WAIT)
        await expect(page.locator("#dropdown-toggle-count")).to_have_text(
            "Dropdown toggles: 1",
        )
        await page.locator("#probe-text-primary").click(force=True)
        await expect(page.locator(".dropdown-menu.show")).to_have_count(0)
        await expect(page.locator("#dropdown-toggle-count")).to_have_text(
            "Dropdown toggles: 2",
        )
        if await inner_button.count():
            await inner_button.first.click()
        else:
            await dropdown.click()
        await expect(page.locator(".dropdown-menu.show")).to_be_visible(timeout=_WAIT)
        await expect(page.locator("#dropdown-toggle-count")).to_have_text(
            "Dropdown toggles: 3",
        )
        await page.keyboard.press("Escape")
        await expect(page.locator(".dropdown-menu.show")).to_have_count(0)
        await expect(page.locator("#dropdown-toggle-count")).to_have_text(
            "Dropdown toggles: 4",
        )


async def test_toast_duration_autohide(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/toasts", ".probe-toast-stay")
        auto = page.locator(".probe-toast-auto")
        await expect(auto).to_have_count(1)
        await expect(auto).to_be_visible(timeout=_WAIT)
        await page.wait_for_function(
            "() => { const el = document.querySelector('.probe-toast-auto'); "
            "return el && !el.classList.contains('show') "
            "&& getComputedStyle(el).display === 'none'; }",
            timeout=_WAIT,
        )
        stay = page.locator(".probe-toast-stay")
        await expect(stay).to_have_count(1)
        stay_display = await stay.first.evaluate("el => getComputedStyle(el).display")
        stay_shown = await stay.first.evaluate(
            """el => el.classList.contains('show')
              || getComputedStyle(el).display !== 'none'""",
        )
        assert stay_display != "none" or stay_shown
        assert stay_shown


async def test_toast_timer_survives_unrelated_update(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#btn-toast-auto")
        await page.locator("#btn-toast-auto").click()
        auto = page.locator(".probe-toast-auto")
        await expect(auto).to_be_visible(timeout=_WAIT)
        await page.wait_for_timeout(500)
        await page.locator("#btn-save").click()
        await expect(page.locator("#label-status")).to_have_text("Saved")
        await page.wait_for_function(
            "() => { const el = document.querySelector('.probe-toast-auto'); "
            "return el && !el.classList.contains('show') "
            "&& getComputedStyle(el).display === 'none'; }",
            timeout=_WAIT,
        )


async def test_two_clients_independent(server: str) -> None:
    async with async_playwright() as playwright:
        args = ["--no-sandbox"] if os.environ.get("CI") else []
        browser = await playwright.chromium.launch(args=args)
        context_a = await browser.new_context(
            viewport={"width": 1024, "height": 800},
        )
        context_b = await browser.new_context(
            viewport={"width": 1024, "height": 800},
        )
        page_a = await context_a.new_page()
        page_b = await context_b.new_page()
        try:
            await _goto(page_a, server, "/clicks", "#click-count")
            await _goto(page_b, server, "/clicks", "#click-count")
            await expect(page_a.locator("#click-count")).to_have_text("0")
            await expect(page_b.locator("#click-count")).to_have_text("0")
            await page_a.locator("#btn-clicks").click()
            await expect(page_a.locator("#click-count")).to_have_text("1", timeout=_WAIT)
            await expect(page_b.locator("#click-count")).to_have_text("0")
        finally:
            await context_a.close()
            await context_b.close()
            await browser.close()


async def test_two_clients_have_independent_overlay_roots(server: str) -> None:
    async with async_playwright() as playwright:
        args = ["--no-sandbox"] if os.environ.get("CI") else []
        browser = await playwright.chromium.launch(args=args)
        context_a = await browser.new_context()
        context_b = await browser.new_context()
        page_a = await context_a.new_page()
        page_b = await context_b.new_page()
        try:
            await _goto(page_a, server, "/mode-b", "#btn-open-modal")
            await _goto(page_b, server, "/mode-b", "#btn-open-modal")
            await expect(page_a.locator("#ngbs-overlay-root")).to_have_count(1)
            await expect(page_b.locator("#ngbs-overlay-root")).to_have_count(1)
            await page_a.locator("#btn-open-modal").click()
            await expect(page_a.locator("#ngbs-overlay-root .modal.show")).to_be_visible(
                timeout=_WAIT,
            )
            await expect(page_b.locator("#ngbs-overlay-root .modal.show")).to_have_count(0)
        finally:
            await context_a.close()
            await context_b.close()
            await browser.close()


async def test_mode_b_overlay_css_is_scoped(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#mode-flag")
        outside = await page.evaluate(
            """() => {
              const el = document.createElement('div');
              el.className = 'toast';
              el.id = 'outside-toast-probe';
              el.textContent = 'outside';
              document.body.appendChild(el);
              const style = getComputedStyle(el);
              return {display: style.display, position: style.position};
            }"""
        )
        assert outside == {"display": "block", "position": "static"}


async def test_programmatic_dropdown_open_reaches_client(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#btn-open-dropdown-programmatically")
        await page.locator("#btn-open-dropdown-programmatically").click()
        await expect(page.locator(".dropdown-menu.show")).to_be_visible(timeout=_WAIT)


async def test_offcanvas_close_removes_visibility_override(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#btn-open-offcanvas")
        await page.locator("#btn-open-offcanvas").click()
        await expect(page.locator("#ngbs-overlay-root .offcanvas.show")).to_be_visible(
            timeout=_WAIT,
        )
        await page.keyboard.press("Escape")
        await page.wait_for_function(
            """() => {
              const el = document.querySelector('#ngbs-overlay-root .offcanvas');
              return el && !el.classList.contains('show')
                && getComputedStyle(el).visibility !== 'visible';
            }""",
            timeout=_WAIT,
        )


async def test_static_modal_escape_and_backdrop_rules(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#btn-open-static-modal")
        await page.locator("#btn-open-static-modal").click()
        static_modal = page.locator("#ngbs-overlay-root .modal").filter(has_text="Static modal")
        await expect(static_modal).to_be_visible(timeout=_WAIT)
        await page.keyboard.press("Escape")
        await expect(static_modal).to_have_count(1)
        await page.wait_for_function(
            "() => !document.querySelector('#ngbs-overlay-root .modal.show')",
            timeout=_WAIT,
        )
        await page.locator("#btn-open-static-modal").click()
        await expect(static_modal).to_be_visible(timeout=_WAIT)
        await (
            page.locator("#ngbs-overlay-root .modal")
            .filter(has_text="Static modal")
            .dispatch_event("mousedown")
        )
        await expect(static_modal).to_be_visible(timeout=_WAIT)


async def test_tooltip_string_target_resolves(server: str) -> None:
    async with _chromium() as page:
        target = '[data-ngbs-public-id="probe-tip-target"]'
        await _goto(page, server, "/mode-b", target)
        assert await page.get_attribute(target, "data-ngbs-public-id") == "probe-tip-target"
        await page.locator(target).hover()
        await expect(page.locator("#ngbs-overlay-root .tooltip.show")).to_be_visible(
            timeout=_WAIT,
        )


async def test_dark_theme_overlay(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/mode-b", "#btn-toggle-dark")
        await page.locator("#btn-open-modal").click()
        await page.wait_for_selector("#ngbs-overlay-root", timeout=_WAIT)
        await expect(page.locator("#ngbs-overlay-root .modal.show")).to_be_visible(
            timeout=_WAIT,
        )
        # With the modal open the page layer is deliberately blocked, so the
        # theme flip comes from an in-modal control (a real user path).
        light_background = await page.eval_on_selector(
            "#ngbs-overlay-root .modal-content",
            "el => getComputedStyle(el).backgroundColor",
        )
        light_text = await page.eval_on_selector(
            "#ngbs-overlay-root .modal-content",
            "el => getComputedStyle(el).color",
        )
        assert _norm_color(str(light_background)) == _BODY_BG
        assert _norm_color(str(light_text)) == _BODY_FG

        await page.locator("#btn-toggle-dark-in-modal").click()
        await page.wait_for_function(
            """() => document.getElementById('ngbs-overlay-root')
              ?.getAttribute('data-bs-theme') === 'dark'""",
            timeout=_WAIT,
        )
        theme = await page.get_attribute("#ngbs-overlay-root", "data-bs-theme")
        assert theme == "dark"
        dark_background = await page.eval_on_selector(
            "#ngbs-overlay-root .modal-content",
            "el => getComputedStyle(el).backgroundColor",
        )
        dark_text = await page.eval_on_selector(
            "#ngbs-overlay-root .modal-content",
            "el => getComputedStyle(el).color",
        )
        assert _norm_color(str(dark_background)) == _BODY_FG
        assert _norm_color(str(dark_text)) == "rgb(222,226,230)"
        assert _norm_color(str(dark_background)) != _norm_color(str(light_background))

        await page.locator("#btn-toggle-dark-in-modal").click()
        await page.wait_for_function(
            """() => document.getElementById('ngbs-overlay-root')
              ?.getAttribute('data-bs-theme') === 'light'""",
            timeout=_WAIT,
        )
        restored_background = await page.eval_on_selector(
            "#ngbs-overlay-root .modal-content",
            "el => getComputedStyle(el).backgroundColor",
        )
        restored_text = await page.eval_on_selector(
            "#ngbs-overlay-root .modal-content",
            "el => getComputedStyle(el).color",
        )
        assert _norm_color(str(restored_background)) == _BODY_BG
        assert _norm_color(str(restored_text)) == _BODY_FG


async def test_compat_surface_divergence(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/compat", "#flag-color-error")
        await expect(page.locator("#flag-color-error")).to_have_text(
            "UnsupportedPropError",
        )
        await expect(page.locator("#flag-debounce-error")).to_have_text(
            "UnsupportedPropError",
        )
        await expect(page.locator("#native-color-input")).to_have_count(1)
        await expect(page.locator("input[type='color']")).to_have_count(1)
        await expect(page.locator("#native-debounce-input")).to_have_count(1)
        await expect(page.locator("#flag-button-identity")).to_have_text("True")


async def test_theme_controller_sets_data_bs_theme(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/theme", "#btn-theme-dark")
        anchor = ".ngbs[data-bs-theme]"
        await page.wait_for_selector(anchor, state="attached", timeout=_WAIT)
        assert await page.get_attribute(anchor, "data-bs-theme") == "light"
        await page.locator("#btn-theme-dark").click()
        await page.wait_for_function(
            """() => document.querySelector('.ngbs[data-bs-theme]')
              ?.getAttribute('data-bs-theme') === 'dark'""",
            timeout=_WAIT,
        )
        await page.locator("#btn-theme-light").click()
        await page.wait_for_function(
            """() => document.querySelector('.ngbs[data-bs-theme]')
              ?.getAttribute('data-bs-theme') === 'light'""",
            timeout=_WAIT,
        )


async def test_theme_controller_unscoped_changes_document_theme(server_unscoped: str) -> None:
    async with _chromium() as page:
        await _goto(page, server_unscoped, "/theme", "#btn-theme-dark")
        # The runtime is injected with the page and stamps the document root once
        # the client connects; wait for it rather than racing the websocket.
        await page.wait_for_function(
            "() => document.documentElement.getAttribute('data-bs-theme') === 'light'",
            timeout=_WAIT,
        )
        assert _norm_color(await _css(page, "body", "backgroundColor")) == _BODY_BG
        await page.locator("#btn-theme-dark").click()
        await page.wait_for_function(
            "() => document.documentElement.getAttribute('data-bs-theme') === 'dark'"
        )
        await page.wait_for_function(
            "() => getComputedStyle(document.body).backgroundColor === 'rgb(33, 37, 41)'"
        )
        assert _norm_color(await _css(page, "body", "backgroundColor")) == _BODY_FG
        await page.locator("#btn-theme-light").click()
        await page.wait_for_function(
            "() => document.documentElement.getAttribute('data-bs-theme') === 'light'"
        )
        await page.wait_for_function(
            "() => getComputedStyle(document.body).backgroundColor === 'rgb(255, 255, 255)'"
        )
        assert _norm_color(await _css(page, "body", "backgroundColor")) == _BODY_BG


async def test_theme_swap_creates_client_stylesheet(server: str) -> None:
    async with _chromium() as page:
        await _goto(page, server, "/theme", "#btn-theme-swap")
        await page.locator("#btn-theme-swap").click()
        await page.wait_for_function(
            "() => !!document.getElementById('ngbs-theme-client')",
            timeout=_WAIT,
        )
        content = await page.eval_on_selector("#ngbs-theme-client", "el => el.textContent || ''")
        assert "layer(overrides)" in content
        assert "ngbs-flatly" in content
