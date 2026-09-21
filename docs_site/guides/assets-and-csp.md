# Assets and Content-Security-Policy

By default this library serves Bootstrap, Bootswatch, and icon stylesheets
from files compiled into the package. Pages work offline. `setup` injects
those sheets as layered CSS with stable ids, once per page. `cdn=True`
switches the same pins to CDN URLs when you explicitly want that.

A strict Content-Security-Policy is straightforward in the bundled path:
no extra hosts, no extra font origins, no runtime fetch of CSS. CDN mode
adds the pinned hosts and is the option you have to justify to a CSP
review.

## Bundled assets

`setup(cdn=False)` — the default — injects local builds:

- Bootstrap 5.3.8 (or the chosen Bootswatch 5.3.8 theme)
- the chosen icon set (Bootstrap Icons by default)

Those bytes never leave your process. There is no request to a CDN, to
jsDelivr, or to npm at page load. Air-gapped deployments, `file:` tests,
and CSP `default-src 'self'` all rely on this path.

Do not also link `bootstrap.min.css` from a template. Two copies of Reboot
and utilities on one page is the usual “my padding doubled” failure. Let
`setup` own the sheets.

## CDN mode

```python
from nicegui_bootstrap_components.assets import StyleMode, setup
from nicegui_bootstrap_components.themes import DARKLY

setup(mode=StyleMode.UNSCOPED, theme=DARKLY, icons="bootstrap", cdn=True)
```

`cdn=True` uses each `Theme` and `IconTheme`’s pinned CDN twin instead of
`bundled`. Pins are part of the release; do not rewrite them to `@latest`.
Theme and icons follow the same flag — there is no “bundled theme, CDN
icons” split.

CDN mode requires network access at page load and a CSP that allows those
hosts (`style-src`, `font-src`, and usually `connect-src` if the CDN
probes). Prefer bundled assets unless you have a concrete reason (shared
corporate CDN, inspecting the public pin).

## `setup()`

Process-level entry point, in `nicegui_bootstrap_components.assets`:

```python
from nicegui_bootstrap_components.assets import StyleMode, setup
from nicegui_bootstrap_components.themes import BOOTSTRAP

setup(
    mode=StyleMode.MIXED,
    theme=BOOTSTRAP,
    icons="bootstrap",
    color_mode="auto",
    cdn=False,
    follow_nicegui_dark=True,
)
```

Arguments:

- `mode` — `StyleMode.MIXED` (default) or `StyleMode.UNSCOPED`; see
  [Mixing with NiceGUI pages](mixed-nicegui-pages.md)
- `theme` — a `Theme` or name string; see [Themes](../themes.md)
- `icons` — `"bootstrap"`, `"fontawesome"`, an `IconTheme`, or `None` to
  keep the process default; see [Icons](../icons.md)
- `color_mode` — `"auto"` by default
- `cdn` — `False` by default
- `follow_nicegui_dark` — `True` by default

Call `setup` at process start, not inside a page function. `AssetManager`
holds those defaults and performs the injection; application code should
not construct `AssetManager` itself. Per-client theme state lives on
`ThemeController` (`ensure_theme_bound`, `get_asset_manager`).

## Injected style blocks

Mixed mode injects layered CSS into the page as `<style>` blocks (and,
when needed, companion links for webfonts). Blocks use **stable ids** so a
second injection replaces the first instead of stacking duplicates. That
is what “idempotent per page” means: opening the same page twice, or
calling `setup` twice with the same arguments, does not accumulate sheets.

The injected CSS is the cascade-layer line-up:

```text
@layer theme, base, quasar, nicegui, components, utilities, overrides, quasar_importants;
```

Author overrides belong in `@layer overrides`, not in an unlayered sheet.
See [Mixing with NiceGUI pages](mixed-nicegui-pages.md).

Do not scrape and rewrite these blocks. If you need a different theme or
icon set, call `setup` with new arguments and let the stable ids replace
the previous injection on the next page.

## Content-Security-Policy with bundled assets

Bundled mode makes no external style or font requests. A tight policy can
omit CDN hosts entirely.

Starting point (adjust to your NiceGUI script/socket needs):

```text
default-src 'self';
style-src 'self' 'unsafe-inline';
font-src 'self';
img-src 'self' data:;
script-src 'self' 'unsafe-inline' 'unsafe-eval';
connect-src 'self' ws: wss:;
```

Notes:

- Injected `<style>` blocks are inline. `'unsafe-inline'` on `style-src`
  is the practical default. If your security bar forbids that, hash or
  nonce the injected blocks; stable ids make the *element* stable, but
  the hash follows the *content*, which is stable per theme / mode / icon
  combination for a given release.
- Icon webfonts are same-origin in bundled mode (`font-src 'self'`).
- NiceGUI still needs whatever `script-src` and `connect-src` your version
  uses for Vue and the websocket. This library does not relax those.
- `cdn=True` adds the pinned CSS and font hosts to `style-src` and
  `font-src`. List those hosts explicitly; do not open `https:`.

Refusing `style-src 'unsafe-inline'` without hashes will drop the layered
sheets and you will see unstyled Bootstrap markup next to styled Quasar.
That is a CSP miss, not a component bug.

## Serving from your own origin

If you want the bytes on *your* CDN / static host rather than in-package
or a public CDN:

1. Keep `cdn=False` so `setup` still injects the layered, remapped CSS
   the library generated (Reboot mapping, `@layer` order, stable ids).
2. Serve extra copies only if you have a non-library consumer (a raw HTML
   email, a separate static site). Do not link those copies on the NiceGUI
   page.
3. If you must replace the injected href, you are off the supported path:
   mixed-mode layering and Reboot remapping live in the injected content,
   not in a vanilla Bootswatch file on a CDN.

Vanilla `bootstrap.min.css` from your origin is not a drop-in for `setup`.
It is unlayered and un-remapped, and it will fight Quasar the way the
[FAQ](../faq.md) describes.

## Idempotent injection

Injection is per page and keyed by the current `setup` arguments. Repeating
`setup(mode=..., theme=..., icons=..., cdn=...)` with the same values is
safe. Changing them updates process defaults for pages constructed after
the call.

Do not toggle `cdn` per request based on the client’s network. Pick one
mode for the process. Per-request switching would race the stable-id
replacement and produce mixed bundled/CDN sheets on a single page.

## Icons, themes, and color mode together

A typical production call:

```python
from nicegui_bootstrap_components.assets import StyleMode, setup
from nicegui_bootstrap_components.themes import FLATLY

setup(
    mode=StyleMode.MIXED,
    theme=FLATLY,
    icons="bootstrap",
    color_mode="auto",
    cdn=False,
    follow_nicegui_dark=True,
)
```

That combination is offline, CSP-friendly, mixed-mode safe, and aligned
with NiceGUI dark. Browse the same builds on [the demo service](../examples.md).

See also [Themes](../themes.md), [Icons](../icons.md), and
[Mixing with NiceGUI pages](mixed-nicegui-pages.md).
