# Layout

Layout components map onto Bootstrap 5's grid and stack helpers: `Container`,
`Row`, `Col`, and `Stack`. Use them to place content on a twelve-column grid
that responds at the usual breakpoints, or to stack children without dropping
into raw utility classes.

`Container` centers and horizontally pads a section of the page. `Row` wraps
columns so they share a horizontal line. `Col` is a single grid cell, and
`Stack` arranges a bundle of children along one axis.

For the grid to work, keep to two rules: put `Row` and `Col` inside a
`Container` (or use `Stack` for non-grid bundles), and make `Col` the immediate
child of `Row`. Content goes inside the `Col`. The snippets below are the same
sources the demo service runs.

## Basic usage

A `Container` holds a `Row` of `Col` children. `width` is the extra-small width;
`md` (and friends, when you add them) override from that breakpoint up. The example below is half-and-half from `md` and full width on smaller viewports.

{{example:examples/components/layout/simple.py:demo}}

## Row with columns

By default columns share the available width equally. Give a column an explicit
width to change that. The accepted width values are:

- `True` (the default): the column expands to fill the available space.
- `"auto"`: the column takes the natural width of its content.
- An integer `1`–`12`: the column spans that many of the twelve grid columns.
  Use `width=6` for half, `width=4` for a third, and so on.

{{example:examples/components/layout/width.py:demo}}

## Specify order and offset

The `width` argument also accepts a dictionary with `size`, `order`, and
`offset` keys.

- `size` takes the same values as the plain width argument.
- `order` reorders columns. It accepts integers or the strings `"first"` and
  `"last"`. Columns sort numerically, with `"first"` and `"last"` at the
  extremes. Equal orders keep their source order.
- `offset` increases the column's left margin by that many grid columns.

{{example:examples/components/layout/order_offset.py:demo}}

## Specify width for different screen sizes

Bootstrap's grid has six responsive tiers. Use the `xs`, `sm`, `md`, `lg`,
`xl`, and `xxl` keyword arguments to set the size, order, and offset of a
column for a screen size and up. Each takes the same values as `width`.
`width` is shorthand for `xs`; if both are set, `xs` wins.

{{example:examples/components/layout/breakpoints.py:demo}}

## Row without 'gutters'

Rows add horizontal spacing between columns by default. Remove it with `g=0`,
or adjust a single axis with `gx`/`gy`. All three take values 0–5.

{{example:examples/components/layout/no_gutters.py:demo}}

## Vertical alignment

Control vertical alignment with the `align` keyword on either `Col` or its
parent `Row`. A value on the `Col` overrules the row. The options are
`"start"`, `"center"`, and `"end"`.

{{example:examples/components/layout/vertical.py:demo}}

## Horizontal alignment

Control horizontal alignment with the `justify` keyword on `Row`. The options
are `"start"`, `"center"`, `"end"`, `"between"`, `"around"`, and `"evenly"`.

{{example:examples/components/layout/horizontal.py:demo}}

## Using only the grid components

To use the grid without Bootstrap's typography and component CSS, load the
grid-only theme once at application startup instead of the full stylesheet:

```python
from nicegui_bootstrap_components import themes
from nicegui_bootstrap_components.assets import StyleMode, setup

setup(mode=StyleMode.UNSCOPED, theme=themes.GRID)
```

That registers `bootstrap-grid.css` only. Run
`examples/components/layout/grid_only.py` as a script to see it: the file's
`__main__` block performs this setup, then builds the page. To serve the
file yourself instead, download `bootstrap-grid.css` and add a `link` to it
from your page's assets directory.

The snippet and screenshot below are the gallery preview of that page body.
The examples service calls `setup(mode=StyleMode.MIXED)` once for the whole
process and cannot switch stylesheets per route, so this preview is not a grid-only theme.
The bordered cells are still the real `bs.container` / `bs.row` / `bs.col`
example.

{{example:examples/components/layout/grid_only.py:demo}}

## `Stack`ing objects

`Stack` arranges objects along a vertical (default) or horizontal axis. Set
`gap` between 0 and 5 to put a consistent gap between the items.

{{example:examples/components/layout/simple_stack.py:demo}}

Use `direction="horizontal"` for horizontal layouts.

{{example:examples/components/layout/horizontal_stack.py:demo}}

Combine stacks with Bootstrap's spacing utilities for finer control. Here the
middle item is pushed away from its neighbours with `ms-auto` and `mx-auto`:

{{example:examples/components/layout/stack_spacers.py:demo}}

## Notes

These helpers are structural. They have no `n_clicks` and no value, and cannot
take user input. Put interactive callbacks on the controls you place inside the
cells.

## Argument reference

{{apidoc:Row}}
