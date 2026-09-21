# FAQ

Short answers to the questions that come up when this library sits next to
NiceGUI, Quasar, and dash-bootstrap-components. Deeper treatment lives in
[Mixing with NiceGUI pages](guides/mixed-nicegui-pages.md),
[Compatibility](compatibility.md), and [Assets and CSP](guides/assets-and-csp.md).

## Is this a drop-in replacement for dash-bootstrap-components?

No. Prop names, visual structure, and Bootstrap 5 class mapping match
dash-bootstrap-components where those things are portable, so a layout that
was a tree of `dbc.Row` / `dbc.Col` / `dbc.Button` can usually be rewritten
with the `dbc` compat surface or the native `bs` surface. There is no Dash
callback graph, no `Input` / `Output` / `State` decorators, and no
pattern-matching IDs. Event handling is NiceGUI’s: Python handlers,
`bind_value`, and local state. Read [Compatibility](compatibility.md) for
the prop-level mapping and the native-only extensions.

## Why do my Quasar components and Bootstrap components fight?

They share a page and therefore a CSS cascade. Quasar (NiceGUI’s default
widgets) and Bootstrap both define buttons, forms, reboot-like body rules,
and utility classes. Mixed mode — the default — injects this library’s CSS
inside cascade `@layer`s so Quasar keeps precedence where the two collide.
Unscoped mode applies Bootstrap more aggressively to the whole page and is
the wrong default for a mixed UI. Wrap Bootstrap trees in `bs.scope()` and
leave Quasar widgets outside that region. The layer line-up, Reboot
remapping, and the overrides escape hatch are in
[Mixing with NiceGUI pages](guides/mixed-nicegui-pages.md).

## Can I use my existing custom CSS with `!important`?

Not if that CSS is unlayered. Library utilities are injected inside named
layers. Unlayered author CSS, even with `!important`, cannot override those
layered utilities; this is how CSS cascade layers work, not a bug in the
components. The supported escape hatch is to put the same rules in
`@layer overrides`, which the library declares after `utilities`. Example
and the full layer order are in
[Mixing with NiceGUI pages](guides/mixed-nicegui-pages.md). Prefer extra
classes or the component’s `class_name` / `style` props when a one-off
tweak is enough.

## How do I persist input values across page reloads?

Set `persist="local"` or `persist="session"` on the value-carrying control
and give it a public `id`. The library reads and writes that id’s value
through `localStorage` or `sessionStorage`. Restore happens when the
element is created and does **not** fire `on_change`, so a restore cannot
loop into your handler or into a binding. `persist` without a public `id`
is rejected. See the persistence section in [Compatibility](compatibility.md)
for the exact props, and [Callbacks and bindings](guides/callbacks-and-bindings.md)
for how `on_change` and `bind_value` interact with restored values.

## Do tooltips and popovers get clipped inside `overflow: hidden` parents?

No. Tooltips and popovers render in the shared overlay root, so a card,
modal body, or table with `overflow: hidden` does not clip them. Dropdowns
are different: they stay in-flow unless `in_navbar=True` or the library
detects clipping, in which case they portal to the overlay root as well.
If a menu still looks clipped, check whether you are looking at a dropdown
(not a tooltip) and whether a transform on an ancestor creates a containing
block. Overlay z-index values are listed in
[Accessibility](guides/accessibility.md).

## Does it work offline / without a CDN?

Yes. Bundled assets are the default: Bootstrap, every Bootswatch 5.3.8
build, and the chosen icon set are compiled into the package and injected
by `setup`. Nothing in the default path requires network access to a CDN
or to npm. `cdn=True` opts into pinned CDN copies of the same builds when
you explicitly want that. Themes and icons both follow the `cdn` flag; do
not mix. See [Themes](themes.md), [Icons](icons.md), and
[Assets and CSP](guides/assets-and-csp.md).

## Which Bootstrap version?

5.3.8, compiled locally and matched to the Bootswatch 5.3.8 builds shipped
in this package. The pin is recorded in `SUPPORT.md`. dash-bootstrap-components
2.0.4 pins Bootstrap 5.3.6, so minor visual deltas (spacing, color tokens,
control details) are possible and accepted. Do not load a second Bootstrap
copy from a CDN or from NiceGUI extras; two copies of reboot and utilities
on one page is the usual source of “my padding doubled” reports.

## Can I run multiple NiceGUI workers?

No. NiceGUI itself rejects `workers>1` for a multi-process UI: one process
holds the UI, the socket, and the element tree. This library does not add
a workaround. Multiple browser clients on that single process are fine.
If you need throughput, scale work *outside* the UI process (task queues,
APIs) and keep one NiceGUI process as the front door. Trying to run two
UI workers will fail at NiceGUI startup, before any Bootstrap component
is constructed.
