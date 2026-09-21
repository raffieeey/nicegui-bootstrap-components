# Spinner

Spinner is an indeterminate loading indicator. It is the library mapping of
Bootstrap 5 `spinner-border` / spinner utilities, used when work is in flight and
you cannot (or should not) show a percentage.

Use a compact spinner next to a button or a table when a local request is running.
Use the fullscreen form when the whole view is unusable until the request returns.

## Basic usage

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    bs.spinner(color="primary")
```

Pair the spinner with a short status label when the wait can last more than a
moment. A spinner alone does not explain what the user is waiting for.

## Live example

The snippet below is exactly what the demo service runs. The highlighted
`demo()` function is the same source the demo executes, not a rewritten copy.

{{example:examples/components/spinner/fullscreen.py:demo}}

## Options

### Color

`color` applies a Bootstrap theme color to the spinner. `primary` is the default
busy color on light pages. `light` and `dark` exist for contrast on inverted
headers. Match nearby controls so the spinner looks like part of the same toolbar
rather than a second accent.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    bs.spinner(color="primary", size="sm")
    bs.spinner(color="secondary")
```

Color is not a status code. Do not use `danger` to mean "failed"; hide the spinner
and show an alert instead.

### Size

`size` scales the control. A small spinner sits inside buttons, input groups, and
table cells without blowing the row height. The default size is for card bodies and
empty states. Keep the size proportional to the region that is waiting so the
indicator does not dominate the layout.

### Fullscreen

`fullscreen` paints the spinner as a viewport overlay so the user cannot miss that
the page is blocked. Turn it on for initial data loads and for mutations that would
be unsafe to overlap (for example a save that rewrites the form). Leave it off for
inline refreshes.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    bs.spinner(color="primary", fullscreen=True)
```

Fullscreen does not replace a disabled submit button. Still ignore duplicate clicks
in the handler; the overlay is a visual lock, not a queue.

### Spinner versus placeholder

A Spinner says "busy" without promising a shape. A Placeholder says "content of
this size is coming". Use placeholders inside lists and cards, and spinners for
actions and whole-page waits. Combining both in the same slot is noisy.

## Argument reference

{{apidoc:Spinner}}
