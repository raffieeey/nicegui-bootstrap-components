# Card

Card is a bordered content container for a heading, media, body, and optional
footer. It maps to Bootstrap 5's `card` family (`card-header`, `card-body`,
`card-img-top`, `card-footer`, `card-group`). Use it for dashboards, product
tiles, and any repeatable unit that should share a common chrome.

## Basic usage

A card with `body=True` wraps its children in a `card-body` for you. For
anything beyond a single text block, compose the named regions instead.

{{example:examples/components/card/basic_body.py:demo}}

`card` is the snake_case alias for `Card`. `body` defaults to `False`.

## Composition

Build a realistic card from `CardHeader`, `CardImg`, `CardBody`, and
`CardFooter`. Wrap sibling cards in `CardGroup` so they share equal height and
joined borders. `CardImg` takes `src` and `alt`; `top=True` places the image
above the body (`bottom=True` places it below).

{{example:examples/components/card/group_composition.py:demo}}

`CardImgOverlay` layers copy on top of an image when you need a caption over
media. `overlay=True` on `CardImg` is the image-side flag for that layout.
`CardLink` is a link styled for use inside the body; it supports `href`,
`external_link`, `on_click`, and `n_clicks`.

## Colored and outline cards

`color` applies a contextual background. `outline=True` keeps a colored border
and a lighter fill. `inverse=True` switches the inner text to a light tone for
dark backgrounds.

{{example:examples/components/card/colored_outline.py:demo}}

## Argument reference

{{apidoc:Card}}

## Notes

Do not put raw strings directly in a grouping card unless `body=True` (or a
`CardBody`) is there to hold them. Prefer the named subcomponents for anything
you will restyle later. See the compatibility page for how Dash click counters
on `CardLink` are adapted to NiceGUI.
