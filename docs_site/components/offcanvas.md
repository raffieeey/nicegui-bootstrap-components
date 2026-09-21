# Offcanvas

Offcanvas is an edge-docked panel that slides in over the current page. It is the
library mapping of Bootstrap 5 `offcanvas`, and it is meant for navigation drawers,
filter sidebars, and inspector panes that should leave the underlying view visible.

Choose Offcanvas when the extra UI is optional context the user can dismiss. Prefer a
modal dialog when work on the page must pause until the overlay is finished.

## Basic usage

{{example:examples/components/offcanvas/basic.py:demo}}

The panel is a container: put labels, forms, and actions inside the context manager.
Construct it closed (`is_open=False`) if a toolbar button should reveal it later.

## Options

### Placement

`placement` selects the viewport edge that owns the panel. Bootstrap values are
`start`, `end`, `top`, and `bottom`. Horizontal placements suit menus and filters;
`top` and `bottom` suit short action strips.

{{example:examples/components/offcanvas/placement_end.py:demo}}

`start` and `end` follow the document writing direction, so a start drawer stays on
the inline-start edge in both LTR and RTL layouts.

### Backdrop

`backdrop` controls the dimmed layer behind the panel. Leave it on when the drawer
should feel modal: the rest of the page is inactive while the panel is open. Pass a
false value when the user should keep editing the main view, for example a persistent
filter column on a wide breakpoint.

A static-style backdrop (when the implementation allows it) keeps the dimmer visible
without closing the panel on an outside click. Use that when accidental dismiss would
lose in-progress input.

### Open state

`is_open` is the Python flag for visibility. It is the source of truth for whether
the panel is on screen. Drive it from buttons, nav links, or application state rather
than fighting the component with extra CSS.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    drawer = bs.offcanvas(
        ui.label("Session"),
        is_open=False,
        placement="start",
        backdrop=True,
    )
    ui.button("Menu")
```

Keep the instance when surrounding controls need to change `is_open` after the
page has been built.

## Argument reference

{{apidoc:Offcanvas}}
