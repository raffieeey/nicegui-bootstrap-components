# Collapse

Collapse shows and hides a block with a height or width transition. It is
Bootstrap 5's `collapse` (including the navbar-collapsible variant). Use it for
disclosure panels, “read more” sections, and the collapsing region of a
responsive navbar — not for mutually exclusive chapters (`Accordion` handles
that).

## Basic usage

`is_open` defaults to `False`. Put the revealed content in a with-block (or pass
child elements). Pair the panel with a `Button` whose handler toggles open
state in your page logic.

{{example:examples/components/collapse/basic_usage.py:demo}}

`collapse` is the snake_case alias for `Collapse`.

## Dimension and navbar

`dimension` defaults to `"height"` (the usual vertical disclosure). Set
`dimension="width"` for a horizontal reveal. `navbar=True` applies the navbar
collapse classes so the panel can sit inside a responsive bar and open as a
block below the toggler on small viewports.

{{example:examples/components/collapse/dimension_navbar.py:demo}}

`on_show`, `on_shown`, `on_hide`, and `on_hidden` are Python hooks for the start
and end of each transition. Register them in the constructor. Shared layout
props `class_name`, `style`, and `id` apply to the collapsing element; give the
panel an `id` when a navbar toggler needs a public target.

## Argument reference

{{apidoc:Collapse}}

## Notes

Collapse is a single panel. If several panels should open independently or as
an exclusive set, use `Accordion` with `always_open` rather than coordinating
many `Collapse` widgets by hand. See the compatibility page for how overlay
lifecycle callbacks are adapted from Dash-style props to NiceGUI.
