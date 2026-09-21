# Carousel

Carousel rotates through a sequence of slides — typically images with an optional
header and caption. It is Bootstrap 5's `carousel`. Use it for hero banners and
short media tours, not as a general-purpose tab control (`Nav` or `Accordion`
fit that job better).

## Basic usage

The carousel is driven by an `items` list of dicts. Each dict may include `src`
and `alt` for the image, plus `header` and `caption` for the overlay copy.
`active_index` selects the first slide (`0` by default).

{{example:examples/components/carousel/basic.py:demo}}

`carousel` is the snake_case alias for `Carousel`.

## Controls, indicators, and interval

`controls` (default `True`) renders the previous/next arrows. `indicators`
(default `True`) renders the dash buttons under the slide. `interval` accepts
an int duration in milliseconds, `False` to disable auto-advance, or `None` to
leave the default. `slide` defaults to `True` for the sliding transition.

{{example:examples/components/carousel/controls_indicators_interval.py:demo}}

`on_change` fires when the active slide changes. `persist` defaults to `"off"`.
Keep every item's `alt` filled in even when the caption already describes the
image — the caption is visible copy, `alt` is for the `img`.

## Argument reference

{{apidoc:Carousel}}

## Notes

This component does not take arbitrary slide children; pass the `items` list.
That keeps the slide markup consistent with Bootstrap's carousel internals.
See the compatibility page for how the native and `dbc` surfaces line up.
