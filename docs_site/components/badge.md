# Badge

Badge is a small count or label that sits next to a heading, a tab, or a button.
It is Bootstrap 5's `badge` (including `rounded-pill` and contextual background
colors). Use it for counts, status chips, and short tags that should not compete
with the surrounding copy.

## Basic usage

The first argument is the badge text. `color` defaults to `"secondary"`. Wrap
construction in `bs.scope()` so the Bootstrap stylesheet is applied. The
snippets below are the same sources the demo service runs.

{{example:examples/components/badge/simple.py:demo}}

`badge` is the snake_case alias for `Badge`.

## Badge sizing

Badges scale to match the size of their parent through relative font sizing.

{{example:examples/components/badge/size.py:demo}}

## Background colors

Use the `color` argument for one of Bootstrap's contextual color classes.

{{example:examples/components/badge/color.py:demo}}

## Text colors

`text_color` overrides the foreground token when the background would otherwise
hide the label.

{{example:examples/components/badge/text_color.py:demo}}

## Pill badges

Set `pill=True` for the fully rounded chip.

{{example:examples/components/badge/pills.py:demo}}

## Positioning

Use Bootstrap's position utility classes to put a badge in the corner of a link
or button.

{{example:examples/components/badge/positioned.py:demo}}

## Links

Add `href` to create actionable badges with hover and focus states. Bootstrap 5
underlines links by default; `text-decoration-none` overrides that.

{{example:examples/components/badge/links.py:demo}}

## Argument reference

{{apidoc:Badge}}

## Notes

Badges are phrasing content: pass a short string, not a nested layout. Pair a
badge with a heading or a nav label rather than using it as a standalone button
unless you also pass `href` or `on_click`. Shared props `class_name`, `style`,
and `id` work as elsewhere in the library.
