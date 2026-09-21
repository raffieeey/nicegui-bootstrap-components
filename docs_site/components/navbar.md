# Navbar

`Navbar` is Bootstrap 5's site header: brand on one side, collapsible links on
the other, optional fixed or sticky positioning. The family is `Navbar`,
`NavbarBrand`, `NavbarToggler`, and `NavbarSimple`. Use `NavbarSimple` when
you want brand plus collapse without assembling the pieces; use the parts when
you need custom inner layout.

## Basic usage

`NavbarSimple` takes a `brand`, optional `brand_href`, and link children. Set
`expand` to a breakpoint so the toggler appears below that width.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    with bs.navbar_simple(
        brand="Demo",
        brand_href="/",
        color="dark",
        dark=True,
        expand="lg",
    ):
        bs.nav_link("Home", href="/", active=True)
        bs.nav_link("Docs", href="/docs")
```

## Live example

The snippet below is exactly what the demo service runs. The highlighted
`demo()` function is the same source the demo executes, not a rewritten copy.

{{example:examples/components/navbar/fixed_sticky.py:demo}}

## Options

### expand, fixed, and sticky

On both `Navbar` and `NavbarSimple`:

- `expand` is `True` (always expanded), `False` (always collapsed to the
  toggler), or a breakpoint string such as `"sm"`, `"md"`, `"lg"`, `"xl"`.
  `NavbarSimple` defaults to `True`.
- `fixed` is `"top"` or `"bottom"` and takes the bar out of flow.
- `sticky` is `"top"` and keeps the bar in flow until it pins.

Do not set `fixed` and `sticky` together. When the bar is `fixed`, add top
padding on the page content so the first heading is not hidden underneath.

### Navbar, NavbarBrand, NavbarToggler

Assemble the chrome yourself when the simple helper is too opinionated.
`Navbar` accepts `color`, `dark`, `expand`, `fixed`, `sticky`, plus `tag`
(default `"nav"`) and `role`. `NavbarBrand` is the name or logo; `href` and
`external_link` control the destination. `NavbarToggler` points `target` at
the collapsible region (pass the component when you have it). The toggler is a
button (`type="button"` by default) with `on_click` and `n_clicks`.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    with bs.navbar(color="light", expand="md", sticky="top"):
        bs.navbar_brand("Demo", href="/")
        bs.navbar_toggler()
```

### NavbarSimple extras

`NavbarSimple` also accepts `brand_external_link`, `brand_style`, `fluid` for
a full-width inner container, `links_left` to put the links before remaining
content, and `is_open` for the collapse state. `dark` pairs with a dark
`color` so brand and toggler contrast correctly.

## Notes

`NavbarToggler` exposes `n_clicks` and `on_click`. The NiceGUI-facing API is
the callable; treat the counter as adapted DBC state rather than something to
poll. Link navigation still goes through `href` on `NavbarBrand` and
`NavLink`.

## Argument reference

{{apidoc:Navbar}}
