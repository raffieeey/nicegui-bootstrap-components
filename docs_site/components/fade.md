# Fade

`Fade` exposes Bootstrap 5's fade transition as a layout wrapper. Children are
shown or hidden with the standard opacity animation instead of an instant swap.
Use it for lightweight enter and leave motion on ordinary page regions when a
modal, collapse, or overlay would be too heavy.

## Basic usage

Construct `bs.fade` (the snake_case alias of `bs.Fade`) inside `bs.scope()` and
place the animated subtree in the context manager. `is_in` and `appear` are
passed at construction.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    with bs.fade(is_in=True, appear=True):
        ui.label("This block uses the Bootstrap fade transition.")
```

## Options

### is_in

`is_in` is the visibility flag. When true, the wrapper displays its children
after the enter transition. When false, it runs the leave transition and hides
them. Drive the flag from the same Python state you use for the rest of the
page; `Fade` does not open itself.

### appear

`appear` controls the first paint only. When true, the enter animation also
runs as the component is mounted, so the content eases in rather than starting
fully opaque. When false, the initial frame skips that animation, which is the
right choice for content that should already be on screen when the page loads.

Use `appear` for optional asides, empty states that populate after a fetch, or
onboarding panels. Leave it off when animating in would delay something the
user is already looking for.

## Composition

`Fade` is a low-level primitive. Alerts, toasts, and overlays implement their
own show and hide behavior; wrapping those again in `Fade` stacks two
transitions and is rarely what you want. Nest `Fade` around ordinary text,
forms, or grid columns when you need the animation without overlay semantics.

Keep the faded subtree small. Animating a large grid or a whole navbar is
harder to follow than fading the panel that actually changed.

## Notes

Interactive wiring follows NiceGUI, not a browser click counter. `Fade` has no
`n_clicks` callback. Pair it with a `bs.button(..., on_click=...)` (or any
other control that exposes a Python callable) and pass a new `is_in` value
when the page rebuilds or when you assign open state on the element.

## Argument reference

{{apidoc:Fade}}
