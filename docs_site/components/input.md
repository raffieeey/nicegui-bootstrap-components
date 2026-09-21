# Input

`Input` is the Bootstrap 5 text control: a native `<input>` with form styling,
validation classes, and NiceGUI value binding. Use it for short values — names,
emails, numbers, passwords — and switch to `Textarea` when the user needs more
than one line.

## Basic usage

`bs.input` is the snake_case alias of `bs.Input`. Pair it with `Label` for an
accessible name; `Input` itself has no `label` argument. All examples run
inside `bs.scope()`.

{{example:examples/components/input/labeled_name.py:demo}}

## Live example

The snippet below is exactly what the demo service runs. The highlighted
`demo()` function is the same source the demo executes, not a rewritten copy.

{{example:examples/components/input/debounce_modes.py:demo}}

## Options

### placeholder, type, and size

`placeholder` is the empty-state hint. `type` defaults to `"text"` and accepts
the usual HTML types (`email`, `password`, `number`, `search`, and so on).
`size` is the Bootstrap control size (`sm` / `lg`), not the HTML `size`
attribute — that is `html_size`. For numeric types, `min`, `max`, and `step`
pass through to the DOM.

{{example:examples/components/input/placeholder_type_size.py:demo}}

### debounce

`debounce` controls how often the Python value updates while the user types.
`False` (the default) publishes without an extra delay. `True` coalesces
updates. An integer is a millisecond delay, which is the usual choice for live
filtering or anything that hits the server on each keystroke.

### Validation and state

`valid` and `invalid` apply Bootstrap validation classes. Compose them with
`FormFeedback` as shown on the [Form](form.md) page. `required`, `disabled`,
`readonly` / `read_only`, `maxlength`, `pattern`, `autocomplete`, `name`, and
`list` map to the native attributes. `plaintext` renders a read-looking control
for review layouts.

### Value and events

`value` is the current string or number. `on_change` fires as the value
publishes (subject to `debounce`). `on_submit` fires when the control submits
— typically Enter in a text field — and `n_submit` counts those events.
`on_blur` / `n_blur` track focus leaving the control. `persist` defaults to
`"off"`.

## Notes

Counters such as `n_submit` and `n_blur` exist for DBC-style state, but the
NiceGUI-facing API is the Python callable: `on_change`, `on_submit`, and
`on_blur`. Bind with `.value` / `bind_value` the same way you would for other
NiceGUI value elements. The root tag is the native control, so form labels
should point `html_for` at the `Input` `id`.

## Argument reference

{{apidoc:Input}}
