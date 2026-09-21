# Dropdown Menu

Dropdown menu is a toggle plus a floating list of actions. It maps to Bootstrap
5's dropdown (`dropdown-toggle`, `dropdown-menu`, `dropdown-item`). Use it for
overflow actions, per-row menus, and navbar account menus — not for primary
navigation that should stay visible.

## Basic usage

Set `label` on `DropdownMenu` for the toggle text, then nest `DropdownMenuItem`
children. An item can be a regular row, a header (`header=True`), or a
separator (`divider=True`). `color` defaults to `"secondary"`; `caret` defaults
to `True`.

{{example:examples/components/dropdown_menu/basic_usage.py:demo}}

`dropdown_menu` and `dropdown_menu_item` are the snake_case aliases for
`DropdownMenu` and `DropdownMenuItem`.

## Direction and navbar placement

`direction` defaults to `"down"`. Bootstrap 5 also accepts `"up"`, `"start"`,
and `"end"` for dropup and sideways menus. Set `in_navbar=True` when the
control lives inside a navbar so alignment and wrapping match the bar.
`align_end=True` right-aligns the menu with the toggle. `nav=True` styles the
toggle as a nav link; `group=True` sits the toggle in a button group.

{{example:examples/components/dropdown_menu/direction_and_navbar.py:demo}}

`size` sizes the toggle (`"sm"`, `"lg"`, or `None`). `disabled=True` disables
the toggle. `toggle_class_name` and `toggle_style` target the toggle button
rather than the outer wrapper. `on_toggle` observes open/close. Items accept
`href`, `disabled`, `active`, `n_clicks`, and `toggle` (default `True`, which
closes the menu after a click).

## Argument reference

{{apidoc:DropdownMenu}}

## Notes

Older dash-bootstrap-components props `right` and `addon_type` were removed;
the compat surface rejects them. Prefer `align_end` and `direction` instead.
Item click counts follow the same NiceGUI adaptation as other clickable
components — see the compatibility page. Keep headers and dividers as their
own `DropdownMenuItem` children rather than encoding them in the parent.
