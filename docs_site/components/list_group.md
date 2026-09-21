# ListGroup

`ListGroup` is Bootstrap 5's list group: a vertical list of related rows for
navigation, settings, or compact results. Use it when each child is a peer item
rather than a paragraph of copy or a grid cell.

## Basic usage

Fill the group with `ListGroupItem` children. Text-only items are fine; wrap
richer rows in the same item component so spacing and borders stay consistent.

{{example:examples/components/list_group/basic.py:demo}}

## Options

### flush

`flush=True` drops the outer border and radius so the list can sit flush
against a card body, a sidebar, or the edge of a column. The items keep their
separators; only the group's chrome goes away.

{{example:examples/components/list_group/flush.py:demo}}

### numbered

`numbered=True` renders an ordered list group. Bootstrap draws the index; you
still pass `ListGroupItem` children, not raw strings at the group level. Use
this for ranked results or step summaries where the order is the point.

{{example:examples/components/list_group/numbered.py:demo}}

`flush` and `numbered` combine when you want ordered rows inside a card.

### ListGroupItem

Each row is a `ListGroupItem`. Keep one idea per item. Nest labels, badges, or
short buttons inside the item when the row needs more than a line of text, but
do not place a `ListGroup` inside another `ListGroup` — nest a new group in a
column instead.

## Notes

`ListGroup` is structural. Item-level clicks, if you add them, belong on
buttons or links inside the item and use NiceGUI `on_click` callables rather
than an `n_clicks` counter on the group.

## Argument reference

{{apidoc:ListGroup}}
