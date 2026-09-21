# Accordion

Accordion stacks collapsible panels so related copy stays compact until the reader
opens a header. It is the NiceGUI surface for Bootstrap 5's accordion
(`accordion` / `accordion-item`). Use it for FAQs, settings groups, and any long
page where several sections should share one vertical footprint.

## Basic usage

Nest `AccordionItem` children inside `Accordion`. Pass `title` for the clickable
header and put the panel body in the item (a with-block or child elements). Set
`item_id` when you need to address a panel from Python. The snippets below are
the same sources the demo service runs.

{{example:examples/components/accordion/simple.py:demo}}

The snake_case names `accordion` and `accordion_item` are aliases for `Accordion`
and `AccordionItem`.

## Start collapsed

Pass `start_collapsed=True` to close every panel on first render. Without it the
first item is open by default.

{{example:examples/components/accordion/collapsed.py:demo}}

## Flush

`flush=True` drops the outer border and radius so the stack can sit flush
against a parent edge.

{{example:examples/components/accordion/flush.py:demo}}

## Callbacks

Each item can be assigned a stable `item_id`, which the `active_item` value and
`on_change` use to say which panel is open. Items without an explicit id are
labelled `item-0`, `item-1`, and so on.

{{example:examples/components/accordion/callback.py:demo}}

## Always open

Set `always_open=True` to allow several panels to stay open together.

{{example:examples/components/accordion/always_open.py:demo}}

With `always_open=True`, `active_item` is a list of ids.

{{example:examples/components/accordion/always_open_callback.py:demo}}

## Argument reference

{{apidoc:Accordion}}

## Notes

`AccordionItem` also accepts `title_class_name` for the header control, plus the
shared layout props `class_name`, `style`, and `id`. `persist` defaults to
`"off"`. Give each item a stable `item_id` if you drive `active_item` from
Python. Header click counts from Dash are not a separate accordion prop here;
interactive wiring follows NiceGUI handlers. See the compatibility page for how
Dash-style props are adapted.
