# Mixing with NiceGUI pages

NiceGUI pages already load Quasar. This library adds Bootstrap 5 on the same
document. The two toolkits both style buttons, forms, and the document root,
so coexistence is an explicit mode, not an accident. Mixed mode is the
default: library CSS is injected inside cascade layers, Bootstrap Reboot is
remapped so it does not clobber NiceGUI page defaults, and `bs.scope()` marks
the region where Bootstrap components render.

Call `setup` once at process start, then wrap Bootstrap trees in `bs.scope()`.
Leave Quasar / NiceGUI widgets outside that region.

## Style modes

`StyleMode` lives in `nicegui_bootstrap_components.assets`:

```python
from nicegui_bootstrap_components.assets import StyleMode, setup
from nicegui_bootstrap_components.themes import BOOTSTRAP

setup(mode=StyleMode.MIXED, theme=BOOTSTRAP)
# setup(mode=StyleMode.UNSCOPED, theme=BOOTSTRAP)
```

`StyleMode.MIXED` (also `"mixed"`) injects Bootstrap inside `@layer`s so
Quasar keeps precedence where the two collide. Use it on any page that still
has NiceGUI widgets (`ui.button`, `ui.input`, `ui.table`, …) next to
Bootstrap components.

`StyleMode.UNSCOPED` applies Bootstrap more aggressively to the whole page.
Reboot-like document rules and utilities leak onto Quasar widgets. Use it
only when the page is entirely Bootstrap (or you are prepared to restyle
every NiceGUI control). Mixed is the default and the correct choice for a
hybrid app.

`setup` is idempotent per page. Switching `mode` changes subsequent pages
in that process; do not expect a live page to restyle in place.

## Scoping with `bs.scope`

`with bs.scope():` marks a region where Bootstrap components render.
Unscoped Quasar / NiceGUI UI is untouched:

```python
from nicegui import ui
from nicegui_bootstrap_components import bs
from nicegui_bootstrap_components.assets import StyleMode, setup

setup(mode=StyleMode.MIXED)

@ui.page("/")
def page() -> None:
    ui.label("Quasar / NiceGUI label")
    ui.button("Quasar button")
    with bs.scope():
        bs.button("Bootstrap button", color="primary")
```

Put only Bootstrap trees inside the scope. Nesting NiceGUI widgets inside
`bs.scope()` is allowed by the DOM but they will sit in a Bootstrap-styled
subtree; mixed-mode layers still protect them from the worst collisions,
yet spacing and font inheritance can change. Prefer sibling regions: NiceGUI
chrome outside, Bootstrap body inside.

`bs.scope()` is a context manager and composes with component `with` blocks
(`with bs.card():`, `with bs.modal():`, and so on). You do not need a scope
per component; one scope around the Bootstrap island is enough.

## CSS layer order

Mixed mode injects the library’s stylesheets into named cascade layers.
The line-up is:

```text
@layer theme, base, quasar, nicegui, components, utilities, overrides, quasar_importants;
```

Meaning of each layer, in order:

- `theme` — Bootswatch / Bootstrap custom properties and theme tokens
- `base` — remapped Reboot (see below), not naked `html` / `body` rules
- `quasar` — Quasar’s normal (non-`!important`) rules, slotted so mixed
  pages keep Quasar look for NiceGUI widgets
- `nicegui` — NiceGUI page defaults
- `components` — Bootstrap component classes (`btn`, `card`, `nav`, …)
- `utilities` — Bootstrap utilities (`m-0`, `d-flex`, `text-end`, …)
- `overrides` — author escape hatch; write your exceptions here
- `quasar_importants` — Quasar `!important` rules, kept so Quasar wins
  the collisions mixed mode is designed to tolerate

Later layers win for normal declarations. That is why `overrides` can beat
`utilities` without fighting Quasar’s important rules, and why unlayered
author CSS is the wrong place for overrides.

Do not redeclare this `@layer` order in your own sheet with a different
sequence. A second `@layer` statement that names the same layers can
reorder them for the whole document.

## Reboot mapping

Bootstrap Reboot sets `html` / `body` box-sizing, font, and margin defaults.
Applied unscoped, those rules clobber NiceGUI page defaults (font family,
background, box-sizing on `#app`). Mixed mode remaps Reboot so the same
reset applies where Bootstrap components need it and does not rewrite the
NiceGUI document root.

You should not import `bootstrap-reboot.css` yourself. You should not add
a second `body { font-family: … }` unlayered sheet to “undo” Reboot; that
is the collision mixed mode already prevents. If a specific Bootstrap
island must use Reboot’s font stack, set it on the scoped root via
`class_name` or via `@layer overrides`, not on `html` / `body`.

Unscoped mode does **not** remap Reboot as conservatively. That is the
main reason a hybrid page should not use `StyleMode.UNSCOPED`.

## Unlayered author CSS

The tradeoff of cascade layers: unlayered author CSS cannot override
layered library utilities.

Bootstrap utilities often carry `!important`. Those declarations live in
`@layer utilities`. An unlayered sheet such as:

```text
.btn-primary { background: #123456 !important; }
```

does not win, because layered `!important` utilities sit above unlayered
`!important` in the cascade. Specificity and source order will not save
you. This surprises teams who brought a Dash stylesheet that relied on
unlayered `!important`.

Fixes that do **not** work:

- raising specificity (`.wrapper .btn-primary { … !important; }`)
- loading the sheet later in `<head>`
- adding `!important` that was not there before

The fix that does work is the `overrides` layer, next section.

## The `layer(overrides)` CSS injection

The library declares an empty-at-first `overrides` layer after `utilities`.
Author rules injected into that layer participate in the same cascade as
the library and can replace utility and component declarations.

Inject CSS into `@layer overrides` (the `layer(overrides)` escape hatch):

```python
from nicegui import ui

ui.add_css(
    """
@layer overrides {
  .btn-primary {
    letter-spacing: 0.02em;
  }
  .card {
    border-radius: 0.75rem;
  }
}
"""
)
```

Rules inside `@layer overrides` are ordinary CSS. You do not need
`!important` unless you are overriding a utility that itself uses
`!important`; prefer extra classes when a one-off is enough.

Keep overrides small. A second design system dumped into `overrides` will
fight Bootstrap the same way unlayered CSS used to fight Quasar. Theme
tokens belong in a `Theme` (see [Themes](../themes.md)), not in a
wall of overrides.

## A complete mixed page

```python
from nicegui import ui
from nicegui_bootstrap_components import bs
from nicegui_bootstrap_components.assets import StyleMode, setup
from nicegui_bootstrap_components.themes import BOOTSTRAP

setup(mode=StyleMode.MIXED, theme=BOOTSTRAP)

ui.add_css(
    """
@layer overrides {
  .btn-primary {
    letter-spacing: 0.02em;
  }
}
"""
)

@ui.page("/")
def page() -> None:
    ui.label("NiceGUI chrome")
    with bs.scope():
        bs.button("Bootstrap button", color="primary")
```

Call `setup` at import time (or in the process entrypoint), not inside the
page function. Page functions run per visit; `setup` is process-level and
already idempotent per page for the injected `<style>` blocks.

## When to use unscoped mode

Use `StyleMode.UNSCOPED` when:

- the page has no Quasar / NiceGUI widgets you care to preserve
- you are porting a Dash layout that assumed document-wide Bootstrap
- you have tested Reboot against your chrome and accepted the drift

Even then, `bs.scope()` remains useful as a grouping construct, but it is
no longer what protects Quasar. Switch back to mixed as soon as a NiceGUI
widget reappears on the page.

See also [FAQ](../faq.md), [Assets and CSP](assets-and-csp.md), and
[Themes](../themes.md).
