# Popover

Popover is a small overlay with optional header and body text, anchored to a target
control. It is the library mapping of Bootstrap 5 `popover`, used for richer hints
than a Tooltip: short explanations, confirmations, and extra fields that should not
navigate away.

Use a Popover when the extra copy needs structure (a title plus a body) or a click
trigger. Use a Tooltip when a single phrase on hover or focus is enough.

## Basic usage

{{example:examples/components/popover/basic_usage.py:demo}}

Compose the overlay with `PopoverHeader` and `PopoverBody` children. The popover is
not laid out in the button's parent; it is mounted on the shared overlay root
(portal) so it can escape overflow and stacking contexts.

## Options

### Header and body composition

Pass a `PopoverHeader` for the title row and a `PopoverBody` for the main copy.
Either piece can be omitted when you only need one of them, but the pair is the
usual pattern because it matches the Bootstrap popover anatomy readers already know.

{{example:examples/components/popover/header_body.py:demo}}

Keep the body short. If the content needs a form or a long list, an Offcanvas or a
modal is a better host.

### Target

`target` accepts either a public id string or an element reference. Passing the
widget you just created is the straightforward path. Passing a public id is useful
when the trigger is declared elsewhere in the page and you only have its id at
composition time.

{{example:examples/components/popover/target_id.py:demo}}

The overlay always lives in the shared overlay portal, not inside the target. Do
not try to position it with parent-relative CSS; `placement` is the supported hook.

### Placement

`placement` is the preferred side of the target: `top`, `bottom`, `left`, `right`,
and the Bootstrap start/end variants. The popover may flip if there is not enough
space. Pick the side that does not cover the control the user just used.

### Trigger

`trigger` chooses the gesture that opens the overlay. `click` is the default for
popovers because the content is richer than a tooltip. `hover` and `focus` are
available when the copy is a hint rather than an action. Avoid hover-only triggers
on touch-first pages.

## Argument reference

{{apidoc:Popover}}
