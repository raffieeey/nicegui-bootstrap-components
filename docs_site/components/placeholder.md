# Placeholder

Placeholder draws a content-shaped loading skeleton. It is the library mapping of
Bootstrap 5 `placeholder` utilities, used to reserve layout while data is in flight
so the page does not jump when the real content arrives.

Reach for Placeholder when you know the approximate shape of the result (a title, a
few lines, a card body). Use a Spinner when the wait is indeterminate and there is
no layout to preserve.

## Basic usage

{{example:examples/components/placeholder/basic.py:demo}}

Render one or more placeholders in the slot that will hold the real content, then
replace them when the request finishes. They are decorative: they should not be the
only indication that work is happening if the wait can fail.

## Options

### Animation

`animation` selects the Bootstrap placeholder motion. A glow pulse is the usual
choice for cards and list rows; a wave animation reads well on wide blocks such as
table bodies. Disable animation when motion would compete with nearby live content
or when the user has requested reduced motion at the page level.

{{example:examples/components/placeholder/animation.py:demo}}

Keep the animation consistent inside a single loading region so the skeleton reads
as one surface rather than a mix of effects.

### Color

`color` applies a Bootstrap theme color to the skeleton. `secondary` and `light`
are quiet defaults on white cards. Stronger colors (`primary`, `info`) work when the
placeholder sits on a tinted header or a dark well. Avoid using color as the only
loading signal; the animation already does that job.

### Size

`size` controls how large the skeleton paints, matching Bootstrap placeholder
sizing. Use a large size for titles and hero lines, and a smaller size for captions,
meta rows, and compact table cells. Mixing sizes in one card is useful when you are
mirroring a heading-plus-body layout.

{{example:examples/components/placeholder/size.py:demo}}

Stack several placeholders with different sizes to sketch a paragraph. Keep the
count close to the real content so the transition from skeleton to data is small.

### Loading regions

Placeholders belong in the same container that will hold the loaded widgets. Do not
park them in a toast or a floating overlay; that hides the layout they are supposed
to protect. When a whole page is waiting and has no structure yet, a Spinner is the
clearer signal.

## Argument reference

{{apidoc:Placeholder}}
