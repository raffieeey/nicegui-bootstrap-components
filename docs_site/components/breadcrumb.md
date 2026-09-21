# Breadcrumb

Breadcrumb shows the path from the site root to the current page. It is Bootstrap
5's `breadcrumb` (a `nav` landmark with an inner list). Use it on nested
workspaces, documentation trees, and any view where the reader may need to step
up one or more levels.

## Basic usage

Pass `items` as a list of dicts. Each dict uses `label` for the visible text,
optional `href` for a link, and `active=True` for the current page (typically
the last crumb, rendered without a link).

{{example:examples/components/breadcrumb/basic.py:demo}}

`breadcrumb` is the snake_case alias for `Breadcrumb`. The root tag defaults to
`"nav"` so the trail is exposed as a navigation landmark.

## Item styling

`item_class_name` and `item_style` apply to every crumb. Use them for spacing or
type tweaks that should not live on the outer `nav`. Keep per-item meaning in
the dicts (`label`, `href`, `active`) rather than trying to encode it in CSS.

{{example:examples/components/breadcrumb/item_styling.py:demo}}

Omit `href` on intermediate crumbs if that level is not a real route. Do not
mark more than one item `active`. Shared layout props `class_name`, `style`, and
`id` land on the outer element.

## Argument reference

{{apidoc:Breadcrumb}}

## Notes

Breadcrumbs are a trail, not a primary menu — keep `Nav` / `Navbar` for the main
information architecture. Item dict keys follow the dash-bootstrap-components
shape (`label`, `href`, `active`) so ports from DBC stay mechanical. See the
compatibility page for surface differences.
