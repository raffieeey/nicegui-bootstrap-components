# Button

Button is the standard action control: submit, cancel, open a dialog, navigate.
It maps to Bootstrap 5's `btn` (contextual colors, outline variants, size
modifiers). Reach for it whenever the reader must trigger a command; use a link
styled as a button only when the action is navigation.

## Basic usage

The first argument is the label. `color` defaults to `"primary"`. Register
`on_click` in the constructor — listeners are not attached later at class level.

{{example:examples/components/button/basic.py:demo}}

`button` is the snake_case alias for `Button`.

## Live example

The snippets below are exactly what the demo service runs. Each highlighted
`demo()` function is the same source the demo executes, not a rewritten copy.

### Colors

{{example:examples/components/button/colors.py:demo}}

### Outline and sizes

{{example:examples/components/button/outline_sizes.py:demo}}

## Outline, size, and state

`outline=True` draws a bordered button instead of a solid fill. `size` accepts
Bootstrap size tokens such as `"sm"` and `"lg"` (`None` is the default size).
`disabled=True` blocks presses; `active=True` applies the pressed appearance
without changing disabled state. `type` defaults to `"button"` so a button
inside a form does not submit unless you set `type="submit"`.

{{example:examples/components/button/outline_size_state.py:demo}}

## Link buttons

Pass `href` to render an anchor that still looks like a button. `target`,
`download`, and `external_link` apply to that link. Leave `href` unset for a
real `<button>` that fires `on_click`. `n_clicks` starts at `0` and increments
on each press.

{{example:examples/components/button/link_buttons.py:demo}}

## Argument reference

{{apidoc:Button}}

## Notes

`name` and `value` are available when the button participates in a form.
Dash's `n_clicks` is implemented for NiceGUI rather than copied as a Dash
callback input; prefer `on_click` in new code. See the compatibility page for
the native versus `dbc` surfaces. Group related actions with `ButtonGroup`.
