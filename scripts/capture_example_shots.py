"""Capture one screenshot per documented example from the running demo service.

Usage (demo service must be running on ``--base-url``)::

    python scripts/capture_example_shots.py            # examples referenced by docs
    python scripts/capture_example_shots.py --all      # every manifest entry
    python scripts/capture_example_shots.py --ids badge_simple badge_positioned

Screenshots land in ``docs_site/assets/examples/<id>.png`` and are picked up by
the ``{{example:...}}`` documentation directive.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs_site"
OUT_DIR = DOCS_DIR / "assets" / "examples"
REF_RE = re.compile(r"\{\{example:([^:}]+):[^}]+\}\}")

CONTENT_CLIP_JS = """() => {
  const content = document.querySelector('.nicegui-content');
  if (!content) return null;
  const pad = 16;
  const viewportW = document.documentElement.clientWidth;
  const contentRect = content.getBoundingClientRect();
  const fallback = {
    x: Math.max(0, contentRect.x - pad),
    y: Math.max(0, contentRect.y - pad),
    width: Math.min(contentRect.width + pad * 2, viewportW),
    height: contentRect.height + pad * 2,
  };

  const isTransparent = (color) => {
    if (!color || color === 'transparent') return true;
    const inner = /rgba?\\(([^)]+)\\)/.exec(color);
    if (!inner) return false;
    const bits = inner[1].split(/[ ,\\/]+/).filter(Boolean).map(parseFloat);
    return bits.length >= 4 && bits[3] === 0;
  };

  const stylePaints = (s) => {
    if (s.backgroundImage && s.backgroundImage !== 'none') return true;
    if (!isTransparent(s.backgroundColor)) return true;
    if (s.boxShadow && s.boxShadow !== 'none') return true;
    for (const side of ['Top', 'Right', 'Bottom', 'Left']) {
      if (
        (parseFloat(s['border' + side + 'Width']) || 0) > 0 &&
        s['border' + side + 'Style'] !== 'none' &&
        !isTransparent(s['border' + side + 'Color'])
      ) {
        return true;
      }
    }
    return false;
  };

  const isShown = (el) => {
    if (typeof el.checkVisibility === 'function') {
      return el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true });
    }
    const s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && parseFloat(s.opacity) !== 0;
  };

  const centered = (v) =>
    v === 'center' ||
    v === 'end' ||
    v === 'flex-end' ||
    v === 'right' ||
    (v && v.indexOf('space-') === 0);

  const hasHorizontalAlign = (s) => {
    const ta = s.textAlign;
    if (ta === 'center' || ta === 'right' || ta === 'end' || ta === 'justify') return true;
    const display = s.display;
    const dir = s.flexDirection;
    if (display === 'flex' || display === 'inline-flex') {
      if (dir === 'column' || dir === 'column-reverse') return centered(s.alignItems);
      return centered(s.justifyContent);
    }
    if (display === 'grid' || display === 'inline-grid') {
      return centered(s.justifyContent) || centered(s.justifyItems);
    }
    return false;
  };

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  const include = (left, top, right, bottom) => {
    if (!(right > left) || !(bottom > top)) return;
    minX = Math.min(minX, left);
    minY = Math.min(minY, top);
    maxX = Math.max(maxX, right);
    maxY = Math.max(maxY, bottom);
  };

  const includeRect = (r) => include(r.left, r.top, r.right, r.bottom);

  const considerElement = (el) => {
    if (!(el instanceof Element)) return;
    if (/^(SCRIPT|STYLE|LINK|META|NOSCRIPT|TEMPLATE)$/.test(el.tagName)) return;
    if (!isShown(el)) return;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    const fullW = r.width >= contentRect.width - 0.5;
    let painted =
      el.matches(
        'img, svg, canvas, video, iframe, embed, object, input, button, select, textarea, progress, meter, hr, audio',
      ) || stylePaints(s);
    if (!painted) {
      for (const pseudo of ['::before', '::after']) {
        const ps = getComputedStyle(el, pseudo);
        if (ps.content && ps.content !== 'none' && ps.content !== 'normal' && stylePaints(ps)) {
          painted = true;
          break;
        }
      }
    }
    if (painted) includeRect(r);
    if (hasHorizontalAlign(s)) includeRect(r);
    if (!fullW) {
      const ml = parseFloat(s.marginLeft) || 0;
      const mr = parseFloat(s.marginRight) || 0;
      const mt = parseFloat(s.marginTop) || 0;
      const mb = parseFloat(s.marginBottom) || 0;
      if (ml > 0 || mr > 0 || mt > 0 || mb > 0) {
        include(
          r.left - Math.max(0, ml),
          r.top - Math.max(0, mt),
          r.right + Math.max(0, mr),
          r.bottom + Math.max(0, mb),
        );
      }
    }
  };

  const considerTree = (root) => {
    if (!(root instanceof Element)) return;
    considerElement(root);
    root.querySelectorAll('*').forEach(considerElement);
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (!node.nodeValue || !String(node.nodeValue).trim()) continue;
      const parent = node.parentElement;
      if (!parent || !isShown(parent) || parent.closest('script, style, noscript, template')) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      includeRect(range.getBoundingClientRect());
    }
  };

  considerTree(content);

  const overlaySeen = new Set();
  const considerOverlayRoot = (root) => {
    if (!(root instanceof Element) || overlaySeen.has(root)) return;
    overlaySeen.add(root);
    if (content.contains(root)) return;
    if (
      root.matches(
        '.modal-backdrop, .offcanvas-backdrop, .q-dialog__backdrop, .q-drawer__backdrop',
      )
    ) {
      return;
    }
    if (!isShown(root)) return;
    const r = root.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return;
    includeRect(r);
    considerTree(root);
  };

  document
    .querySelectorAll(
      [
        '.modal.show .modal-dialog',
        '.modal.showing .modal-dialog',
        '.modal[open] .modal-dialog',
        '.modal[aria-modal="true"] .modal-dialog',
        'dialog[open]',
        '.offcanvas.show',
        '.offcanvas.showing',
        '.offcanvas[open]',
        '.offcanvas[aria-modal="true"]',
        '.toast.show',
        '.toast.showing',
        '.popover.show',
        '.popover[data-show]',
        '.tooltip.show',
        '.tooltip[data-show]',
        '.q-dialog__inner > *',
        '.q-notification',
        '.q-menu',
        '.q-tooltip',
        '.q-drawer--on-top',
      ].join(','),
    )
    .forEach(considerOverlayRoot);

  if (!Number.isFinite(minX) || maxX <= minX || maxY <= minY) return fallback;
  const x = Math.max(0, minX - pad);
  const y = Math.max(0, minY - pad);
  const width = Math.max(0, Math.min(viewportW, maxX + pad) - x);
  const height = Math.max(0, maxY + pad - y);
  if (width <= 0 || height <= 0) return fallback;
  return { x, y, width, height };
}"""


def documented_sources() -> set[str]:
    """Return every source path referenced by an ``{{example:}}`` directive."""
    sources: set[str] = set()
    for page in DOCS_DIR.rglob("*.md"):
        sources.update(REF_RE.findall(page.read_text(encoding="utf-8")))
    return sources


def manifest_by_source() -> dict[str, dict[str, object]]:
    raw = yaml.safe_load((REPO_ROOT / "examples" / "manifest.yaml").read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("examples", [])
    entries: dict[str, dict[str, object]] = {}
    for item in items:
        if isinstance(item, dict) and item.get("source") and item.get("id"):
            entries[str(item["source"])] = item
    return entries


def select_entries(args: argparse.Namespace) -> dict[str, dict[str, object]]:
    by_source = manifest_by_source()
    if args.ids:
        wanted = {str(e["id"]): e for e in by_source.values() if str(e["id"]) in set(args.ids)}
    elif args.all:
        wanted = {str(e["id"]): e for e in by_source.values()}
    else:
        wanted = {
            str(entry["id"]): entry
            for source in documented_sources()
            if (entry := by_source.get(source))
        }
    return wanted


def capture(base_url: str, entries: dict[str, dict[str, object]]) -> list[tuple[str, str]]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[tuple[str, str]] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 800}, device_scale_factor=2)
        page.emulate_media(reduced_motion="reduce")
        for example_id in sorted(entries):
            route = str(entries[example_id]["route"])
            try:
                page.goto(base_url.rstrip("/") + route, wait_until="load", timeout=30000)
                page.wait_for_function(
                    "() => {const c = document.querySelector('.nicegui-content');"
                    " return c && c.children.length > 0;}",
                    timeout=15000,
                )
                page.wait_for_timeout(1200)
                box = page.evaluate(CONTENT_CLIP_JS)
                target = OUT_DIR / f"{example_id}.png"
                if box and box["width"] > 0 and box["height"] > 0:
                    clip = {
                        "x": box["x"],
                        "y": box["y"],
                        "width": box["width"],
                        "height": box["height"],
                    }
                    page.screenshot(path=str(target), clip=clip)
                else:
                    page.screenshot(path=str(target), full_page=True)
                print(f"ok   {example_id}")
            except Exception as exc:  # noqa: BLE001 - report and keep going
                failures.append((example_id, f"{type(exc).__name__}: {exc}"))
                print(f"FAIL {example_id}: {exc}")
        browser.close()
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--all", action="store_true", help="capture every manifest entry")
    parser.add_argument("--ids", nargs="*", default=None, help="capture only these example ids")
    args = parser.parse_args()

    entries = select_entries(args)
    if not entries:
        print("nothing to capture")
        return 1
    failures = capture(args.base_url, entries)
    print(f"\ncaptured {len(entries) - len(failures)}/{len(entries)}")
    for example_id, message in failures:
        print(f"  failed: {example_id} ({message})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
