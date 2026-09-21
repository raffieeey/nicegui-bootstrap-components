# Alert

Alert is an inline message used for feedback, status, and short notices. It maps
to Bootstrap 5's `alert` component (contextual color classes such as
`alert-success`). Reach for it when you need a prominent, in-flow message rather
than a toast or a modal.

## Basic usage

Pass the message as the child and pick a contextual `color`. Build the widget
inside `bs.scope()` so Bootstrap styles are active on the page. The snippets
below are the same sources the demo service runs.

{{example:examples/components/alert/simple.py:demo}}

`alert` is the snake_case alias for `Alert`. Either name constructs the same
native component; the `dbc` surface follows dash-bootstrap-components naming.

## Link color

The Bootstrap `alert-link` class colors links inside an alert to match the
alert's own color.

{{example:examples/components/alert/link.py:demo}}

## Additional content

Alerts can carry headings, paragraphs, and dividers.

{{example:examples/components/alert/content.py:demo}}

## Dismissing

Set `dismissable=True` to add a dismiss button, or drive `is_open` yourself.
`fade=False` disables the fade animation.

{{example:examples/components/alert/dismissible.py:demo}}

## Automatic dismissal

Pass `duration` (milliseconds) and the alert dismisses itself shortly after it
becomes visible.

{{example:examples/components/alert/auto_dismiss.py:demo}}

## Icons

An icon from Bootstrap Icons (or Font Awesome) can lead the message.

{{example:examples/components/alert/icon.py:demo}}

## Argument reference

{{apidoc:Alert}}

## Notes

Use alerts for durable, in-page status (form errors, empty states, permission
warnings). For ephemeral confirmation after a click, NiceGUI's `ui.notify` is
usually a better fit. Dash-style click counters are not the primary API on this
component; see the compatibility page for how interactive props are adapted to
NiceGUI.
