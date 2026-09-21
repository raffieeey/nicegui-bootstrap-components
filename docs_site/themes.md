# Themes

This library ships every Bootswatch 5.3.8 build compiled locally, together with
Bootstrap itself. Theme stylesheets therefore work offline. No CDN request is
required unless you opt in with `cdn=True`.

Use `setup` to choose a theme once at process start, then render Bootstrap
components inside `bs.scope()`. The same bundled files power [the demo
service](examples.md), including its live theme explorer.

## Selecting a theme

Call `setup` before any page is served. Pass a `Theme` from
`nicegui_bootstrap_components.themes` (or an equivalent name string).

```python
from nicegui import ui
from nicegui_bootstrap_components import bs
from nicegui_bootstrap_components.assets import setup
from nicegui_bootstrap_components.themes import DARKLY

setup(mode="mixed", theme=DARKLY)

with bs.scope():
    bs.button("Darkly themed", color="primary")
```

`mode="mixed"` is the default coexistence mode; see
[Mixing with NiceGUI pages](guides/mixed-nicegui-pages.md). The default theme
is `BOOTSTRAP` (stock Bootstrap 5.3.8). Prefer the imported constant over a
string so a typo fails at import time.

`setup` injects layered CSS with stable element ids and is idempotent per
page. Do not hot-swap themes by editing `<link>` or `<style>` tags yourself;
pass a different `theme=` into `setup` so the asset manager can replace the
injected sheets cleanly. Related knobs (`icons=`, `cdn=`, `color_mode=`) are
documented in [Assets and CSP](guides/assets-and-csp.md).

## Bundled builds and CDN twins

Each `Theme` is a small record with three fields:

- `name` — canonical identifier (`"darkly"`, `"bootstrap"`, …)
- `bundled` — locally compiled stylesheet shipped in this package
- `cdn` — pinned CDN URL for the same Bootswatch (or Bootstrap) build

Offline is the default: the asset manager serves `bundled`. Pass `cdn=True`
to `setup` if you want the pinned CDN copy instead. Icon stylesheets follow
the same rule; see [Icons](icons.md).

Pinned CDN URLs are part of the release. Do not rewrite them to “latest”.
If you must host the CSS yourself, keep `cdn=False` and serve the bundled
file from your origin as described in the assets guide.

## Available themes

Import any of the following from `nicegui_bootstrap_components.themes`. Every
row is a full `Theme` object with a bundled 5.3.8 build and a pinned CDN twin.

| Constant | Name | Character |
| --- | --- | --- |
| `BOOTSTRAP` | bootstrap | Stock Bootstrap 5.3.8. Neutral baseline. |
| `CERULEAN` | cerulean | Calm blue header and links. |
| `COSMO` | cosmo | Open sans, high contrast, Metro-like. |
| `CYBORG` | cyborg | Dark background with bright accents. |
| `DARKLY` | darkly | Dark Bootstrap palette, default dark example. |
| `FLATLY` | flatly | Flat colors, strong headings. |
| `GRID` | grid | Grid-forward Bootswatch 5 variant. |
| `JOURNAL` | journal | Serif news-like headings. |
| `LITERA` | litera | Typographic, generous leading. |
| `LUMEN` | lumen | Light surfaces with soft shadows. |
| `LUX` | lux | Uppercase tracking, elegant. |
| `MATERIA` | materia | Material-inspired elevation. |
| `MINTY` | minty | Mint greens and rounded controls. |
| `MORPH` | morph | Soft neomorphic highlights. |
| `PULSE` | pulse | Purple primary, bold CTAs. |
| `QUARTZ` | quartz | Gradient glass surfaces. |
| `SANDSTONE` | sandstone | Warm earth tones. |
| `SIMPLEX` | simplex | Small-caps headings, compact. |
| `SKETCHY` | sketchy | Hand-drawn borders. |
| `SLATE` | slate | Cool dark greys. |
| `SOLAR` | solar | Solarized dark. |
| `SPACELAB` | spacelab | Silvery buttons and gradients. |
| `SUPERHERO` | superhero | Dark navy with orange. |
| `UNITED` | united | Ubuntu-inspired orange. |
| `VAPOR` | vapor | Vaporwave pinks and teals. |
| `YETI` | yeti | Clean corporate light theme. |
| `ZEPHYR` | zephyr | Breezy blues and large radius. |

Names are case-insensitive when you pass a string into `setup(theme=...)`.
The constants above are the supported set; an unknown name is rejected at
setup time rather than falling back silently.

## Color mode

`setup` also accepts `color_mode` and `follow_nicegui_dark`:

```python
from nicegui_bootstrap_components.assets import StyleMode, setup
from nicegui_bootstrap_components.themes import BOOTSTRAP

setup(
    mode=StyleMode.MIXED,
    theme=BOOTSTRAP,
    color_mode="auto",
    follow_nicegui_dark=True,
)
```

`color_mode="auto"` (the default) lets the page follow the usual light/dark
signal. Set an explicit mode when you need to pin the palette independently
of the operating system. When `follow_nicegui_dark` is true (the default),
Bootstrap’s color mode stays aligned with NiceGUI’s dark-mode flag so a
Quasar dark page and Bootstrap `data-bs-theme` do not drift apart.

Theme CSS and color mode are orthogonal: Darkly is a dark Bootswatch even
in light color mode, and `BOOTSTRAP` still honors `data-bs-theme="dark"`.
Pick the Bootswatch that matches the product, then let `color_mode` handle
the light/dark toggle on top.

## Page-lifetime theme state

Process-level defaults live on `AssetManager` in
`nicegui_bootstrap_components.assets`. Per-client state lives on
`ThemeController` in `nicegui_bootstrap_components.theme`. Application code
normally calls `setup` only. `ensure_theme_bound` and `get_asset_manager`
are the supported helpers if a page needs to re-bind after a custom client
setup; do not construct `AssetManager` or `ThemeController` yourself unless
you are extending the injection pipeline.

Because injection is idempotent per page, repeating `setup` with the same
arguments is safe. Changing `theme`, `icons`, `mode`, or `cdn` replaces the
injected sheets for subsequent pages in that process.

## Theme explorer

Compare palettes against real components on [the demo service](examples.md).
The explorer uses the same bundled 5.3.8 builds this package injects, so
what you see there is what `setup(theme=...)` will serve offline.

See also [Icons](icons.md), [FAQ](faq.md), and
[Assets and CSP](guides/assets-and-csp.md).
