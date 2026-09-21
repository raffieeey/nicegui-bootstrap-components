# Icons

The library bundles two icon stylesheets: Bootstrap Icons (the default) and
Font Awesome (opt-in). Both ship as local files with pinned CDN twins, matching
the theme model in [Themes](themes.md). Offline is the default; `cdn=True`
switches icon CSS (and theme CSS) to the pinned CDN copy.

Icon fonts are style assets, not a component family. You apply CSS classes
in markup. There is no extra runtime or icon-name resolver beyond what the
stylesheet provides.

## Choosing an icon set

Pass `icons=` to `setup` once at process start:

```python
from nicegui_bootstrap_components.assets import setup

setup(mode="mixed", icons="bootstrap")   # or "fontawesome"
```

Equivalent forms using the `IconTheme` constants:

```python
from nicegui_bootstrap_components.assets import setup
from nicegui_bootstrap_components.icons import BOOTSTRAP, FONT_AWESOME

setup(mode="mixed", icons=BOOTSTRAP)
# setup(mode="mixed", icons=FONT_AWESOME)
```

`icons="bootstrap"` (or `BOOTSTRAP`) is the default. `icons="fontawesome"`
(or `FONT_AWESOME`) is opt-in: it injects the Font Awesome stylesheet instead
of, not in addition to, Bootstrap Icons. Pick one set per process so class
names and font files stay consistent across pages.

`None` leaves the process default in place. Call `setup` before serving
pages; later pages reuse the same injected icon sheet.

## Bundled copies and CDN twins

Each `IconTheme` carries:

- `name` — `"bootstrap"` or `"fontawesome"`
- `bundled` — locally compiled stylesheet shipped in this package
- `cdn` — pinned CDN URL for the same build

With `cdn=False` (the default) the asset manager serves `bundled` and the
icon webfonts from this package. No third-party host is contacted. With
`cdn=True`, both the theme and the icon stylesheet use their pinned CDN
URLs. Do not mix a bundled theme with a CDN icon sheet; `setup` applies one
mode to every injected asset. Details and CSP consequences are in
[Assets and CSP](guides/assets-and-csp.md).

## Bootstrap Icons

Bootstrap Icons use the `bi` prefix. The webfont is bundled next to the CSS.
A minimal mark:

```python
from nicegui import ui

alarm = ui.element("i")
alarm.classes("bi bi-alarm")
alarm.props("aria-hidden=true")
```

```html
<i class="bi bi-alarm" aria-hidden="true"></i>
```

Decorative icons should keep `aria-hidden="true"` when the adjacent text
already names the action. If the icon is the only label (an icon-only
control), set an accessible name on the control (`aria-label`, or visible
text inside a `Button`) rather than on the `<i>`.

Class names follow the Bootstrap Icons catalog (`bi-alarm`, `bi-house`,
`bi-chevron-right`, …). The stylesheet maps each class to a code point in
the bundled webfont. Unknown classes render as empty glyphs, not errors.

## Font Awesome

Font Awesome is opt-in because its license terms differ from Bootstrap
Icons. Read the note in the repository `NOTICE` and `SUPPORT.md` files
before shipping it. Typical markup uses the style prefix plus the icon
name:

```python
from nicegui import ui

house = ui.element("i")
house.classes("fa-solid fa-house")
house.props("aria-hidden=true")
```

```html
<i class="fa-solid fa-house" aria-hidden="true"></i>
```

Solid (`fa-solid`), regular (`fa-regular`), and brand (`fa-brands`) prefixes
work only if that style is part of the bundled Font Awesome build this
package injects. Stick to the classes that ship with the bundle; do not
assume a Pro kit or a later major version.

## Using icons in markup

Icons are CSS classes, so they compose with ordinary NiceGUI elements and
with Bootstrap components that accept children or `class_name`:

```python
from nicegui import ui
from nicegui_bootstrap_components import bs
from nicegui_bootstrap_components.assets import setup

setup(mode="mixed", icons="bootstrap")

@ui.page("/")
def page() -> None:
    with bs.scope():
        with bs.button("Alarm", color="primary"):
            ui.element("i").classes("bi bi-alarm me-2").props("aria-hidden=true")
```

Spacing utilities such as `me-2` come from Bootstrap, not from the icon
set. They are available inside `bs.scope()` in mixed mode the same way
other utilities are; see
[Mixing with NiceGUI pages](guides/mixed-nicegui-pages.md).

Prefer a real element (`<i>` or `<span>`) over injecting SVG by hand unless
you need a custom glyph. Custom SVGs bypass the bundled webfont and then
you own contrast, sizing, and CSP `img-src`/`data:` rules yourself.

## License

Bootstrap Icons follow the license recorded for that bundle in `NOTICE`.
Font Awesome is opt-in: do not enable `icons="fontawesome"` in a
distribution until you have read `NOTICE` and `SUPPORT.md`. This page does
not reproduce those terms.

CDN mode does not change the license. It only changes where the bytes are
loaded from. The pinned CDN twin is the same build the package bundles.

## Pairing with themes and CSP

Icons and themes are independent `setup` arguments:

```python
from nicegui_bootstrap_components.assets import setup
from nicegui_bootstrap_components.themes import FLATLY

setup(mode="mixed", theme=FLATLY, icons="bootstrap", cdn=False)
```

Bundled icon webfonts are same-origin, which keeps a strict
Content-Security-Policy simple (`font-src 'self'`). CDN mode requires
allowing the pinned icon host as well. See
[Assets and CSP](guides/assets-and-csp.md) and [FAQ](faq.md).

See also [Themes](themes.md) and [the demo service](examples.md).
