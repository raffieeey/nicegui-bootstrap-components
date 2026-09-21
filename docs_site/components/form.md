# Form

`Form` is the Bootstrap 5 `<form>` wrapper for NiceGUI. It groups labels,
controls, help text, and validation messages so a settings page or wizard step
reads as one submission. Use it when you need native form semantics — submit
handling, `novalidate`, and optional `action` / `method` — rather than a loose
stack of inputs.

## Basic usage

Place labels and controls inside `bs.form`. `prevent_default_on_submit` defaults
to true so the browser does not navigate away; handle the submit in Python.

{{example:examples/components/form/basic_usage.py:demo}}

## Options

### Validation feedback

Compose validation with `Input.valid` / `Input.invalid` and `FormFeedback`.
`FormFeedback.type` selects valid versus invalid styling; `tooltip=True` shows
the message as a tooltip instead of inline text. `novalidate=True` on `Form`
turns off native browser bubbles so these messages are the ones the user sees.

{{example:examples/components/form/validation_feedback.py:demo}}

### Label

`Label` is the Bootstrap form label. `html_for` points at the control `id`.
`hidden` keeps the label available to assistive tech without drawing it.
`check=True` styles a checkbox or radio label. `size`, `align`, `color`, and
the grid keys `width`, `xs`, `sm`, `md`, `lg`, `xl`, and `xxl` let the label
sit in a horizontal layout beside its control.

### FormText and FormFloating

`FormText` is muted help copy under a control; optional `color` overrides the
default hint color. `FormFloating` is the floating-label group. Child order is
control then label and is not reordered for you. Set `html_for` on the floating
wrapper or the label so the pair stays associated.

{{example:examples/components/form/form_floating.py:demo}}

### InputGroup and InputGroupText

Inside a form, `InputGroup` clusters a control with add-on text. Put
`InputGroupText` before the input to prepend, after it to append. `size` on the
group (`sm` / `lg`) scales the whole cluster. See [InputGroup](input_group.md)
for more composition examples.

### Submit wiring

`action` and `method` map to the HTML attributes when you truly want a
browser-level post. `on_submit` is the NiceGUI-facing callback. `n_submit`
counts successful submit events if you need a counter in state, but the
callable is the primary API.

## Notes

DBC-style `n_submit` counters are adapted for NiceGUI: prefer `on_submit` over
polling the counter. There is no separate `n_clicks` on `Form`; use `Button`
click handlers for non-submit actions inside the form.

## Argument reference

{{apidoc:Form}}
