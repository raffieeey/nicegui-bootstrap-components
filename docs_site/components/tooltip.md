# Tooltip

Tooltip is a short overlay anchored to a control, used for a phrase of extra
context. It is the library mapping of Bootstrap 5 `tooltip`, and it is the right
choice when a label, icon button, or truncated value needs a hover or focus hint.

Keep the copy to one line. If you need a title plus a body, or a click-to-open
gesture, use a Popover instead.

## Basic usage

{{example:examples/components/tooltip/basic.py:demo}}

The overlay is not a child of the button in the layout tree. It is mounted on the
shared overlay root (portal) so it can escape overflow hidden and local stacking
contexts.

## Options

### Target

`target` accepts a public id string or an element reference. Passing the widget
directly is the straightforward path right after you create it. Passing a public id
is useful when the trigger lives elsewhere in the page and you only have its id at
composition time.

{{example:examples/components/tooltip/target.py:demo}}

Do not wrap the target in extra positioned divs just to place the tooltip.
`placement` is the supported hook; the portal handles the rest.

### Placement

`placement` is the preferred side of the target: `top`, `bottom`, `left`, `right`,
and the Bootstrap start/end variants. The tooltip may flip if there is not enough
space. Prefer `top` or `bottom` for icon buttons in a toolbar so the hint does not
cover neighboring controls.

### Trigger

`trigger` chooses the gesture that shows the hint. `hover` and `focus` are the
accessible pair for tooltips: pointer users get hover, keyboard users get focus.
A click trigger is closer to popover behavior; use a Popover if the user is meant
to dismiss the overlay deliberately.

### Delay

`delay` is the pause before the tooltip appears, in milliseconds. A small delay
(around 150–300) avoids flashing hints as the pointer crosses a toolbar. Do not
raise the delay so high that keyboard users think the control has no help text.

{{example:examples/components/tooltip/delay.py:demo}}

Tooltips are supplementary. The control must still make sense without the overlay,
because touch and some assistive setups will not see hover content.

## Argument reference

{{apidoc:Tooltip}}
