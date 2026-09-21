# Jumbotron

Jumbotron is not a component in this library. Bootstrap 5 removed the dedicated
jumbotron class, and the matching page here is a **composition recipe**: a
`Card` plus padding and type utilities. Use it for a large welcome callout or
hero block when you want emphasis without a real overlay or navbar.

## Basic usage

Apply Bootstrap spacing and background utilities through `class_name` on
`Card`, then put the heading, lead copy, and actions inside.

{{example:examples/components/jumbotron/basic.py:demo}}

## Options

There is no `Jumbotron` type, so there are no jumbotron-only props. Tune the
recipe with classes on the `Card`:

- Padding: `p-5` (or `p-4` on smaller screens of copy) is the usual hero inset.
- Stacking: `mb-4` separates the callout from the next section.
- Surface: `bg-body-tertiary`, `bg-light`, or a contextual `bg-*` class.
- Corners: `rounded-3` restores the soft hero shape Bootstrap 4 jumbotrons had.

Keep actions as `Button` children (or links) inside the card. The card is a
grouping container; put text in child elements rather than passing a raw string
if you need mixed heading levels.

### Alternate recipe

A bordered, full-width hero is the same pattern with a different class set.
Still a `Card`, still not a separate component.

{{example:examples/components/jumbotron/alternate_recipe.py:demo}}

## Notes

Because this page is a recipe, argument details below are for `Card`. Interactive
pieces you drop in (buttons, inputs) use NiceGUI callables such as `on_click`
and `on_change`; there is no jumbotron-level `n_clicks`.

## Argument reference

{{apidoc:Card}}
