# Accessibility

Bootstrap components are usable with a keyboard and with assistive
technology when the page does not fight them. This library wires focus
restore, Escape, backdrop dismiss, and overlay z-index to Bootstrap 5
conventions. It does not replace an audit. Test with a keyboard only, then
with axe, before you ship.

The repository ships a keyboard release checklist and a visual / a11y test
matrix. Use those as the bar for a change that touches Modal, Offcanvas,
Tabs, DropdownMenu, Accordion, Tooltip, or Popover.

## Focus handling

Modal and Offcanvas move focus into the overlay when they open and restore
it to the opener when they close. Restoration is part of the close path
(Escape, backdrop click, close button, or setting the open state to false).
Do not steal focus in an `on_change` handler that runs on close; you will
race the restore.

While a Modal is open, focus is trapped inside it. Tab and Shift+Tab cycle
through the dialog’s tabbable controls, not through the page behind the
backdrop. Offcanvas follows the same restore rule; treat it as a panel,
not as a second document.

If you open a Modal from a control that is then removed from the DOM, there
is nothing to restore to. Keep the opener mounted, or move focus yourself
to a sensible landmark after close.

Do not set `autofocus` on a hidden field inside a closed Modal. Focus must
not land in `aria-hidden` content.

## Escape and backdrop

Escape closes the top overlay (Modal or Offcanvas) when dismiss-on-escape
is enabled, which is the default. Backdrop click dismisses the same way
when the backdrop is not static. A static backdrop still blocks the page
and still traps focus; it just does not close on outside click.

Order of operations on dismiss:

1. Escape or backdrop click is received.
2. The overlay begins to close.
3. Focus returns to the opener.
4. The page behind is interactive again.

Do not bind a document-level Escape handler that also closes the overlay;
you will double-close or restore focus twice. Use the component’s own
dismiss path.

Tooltips and popovers are not focus traps. They close on Escape when they
are interactive, and they render in the shared overlay root so they are
not clipped by `overflow: hidden` ancestors (see [FAQ](../faq.md)).

## Keyboard navigation

Tabs, DropdownMenu, and Accordion implement the usual Bootstrap / APG
patterns:

- **Tabs** — Left and Right move among tabs (Up and Down when the tab list
  is vertical). Home and End jump to the first and last tab. Tab moves
  from the active tab into that tab’s panel. The active tab is the only
  tab in the tab order; roving tabindex.
- **DropdownMenu** — Enter or Space on the toggle opens the menu. Down
  (and Up) move among items. Enter activates the focused item. Escape
  closes and returns focus to the toggle. Typeahead character search is
  not required of authors; do not break it if the menu provides it.
- **Accordion** — Enter or Space on a header toggles that section. Arrow
  keys move between headers. Focus stays on the header after toggle so
  screen-reader users do not lose their place.

Dropdowns portal to the overlay root when `in_navbar=True` or when clipping
is detected, so keyboard focus is not lost behind a navbar overflow. If you
build a custom toggle, keep it a real `<button>` (or a `Button` component)
so it stays in the tab order.

## One modal at a time

The library enforces a one-modal policy. A second Modal does not stack on
the first. Stacked dialogs create nested focus traps, competing Escape
handlers, and a backdrop pile that no longer matches a single z-index.
Close the open Modal before you open another, or reuse one Modal and swap
its body content.

Offcanvas may be open next to a Modal only if you have checked the focus
order; the default guidance is still one overlay that traps focus at a
time. Confirmation UI belongs *inside* the open Modal, not in a second
dialog on top of it.

## Z-index layering

Overlays share a documented stack. Do not invent new z-index values in
author CSS for these surfaces; you will collide with tooltips or with
NiceGUI’s own menus.

| Surface | z-index |
| --- | --- |
| Backdrop | 5040 |
| Modal | 5055 |
| Tooltip | 5090 |

A tooltip must be able to paint over a modal (hence 5090 > 5055). A modal
must paint over its backdrop (5055 > 5040). Author chrome that uses values
in this band will flicker through overlays; keep page chrome well below
5040.

Dropdowns that portal use the overlay root as well. In-flow dropdowns
(`in_navbar=False` and no clipping) follow the parent stacking context
instead of this table.

If you need a custom overlay, reuse these numbers or sit *between* bands
deliberately. Do not copy Quasar’s z-index scale on top of this one.

## Release checklists

The repository ships:

- a **keyboard release checklist** — Tab order, focus restore, Escape,
  arrow keys for Tabs / DropdownMenu / Accordion, no keyboard trap outside
  an open overlay
- a **visual / a11y test matrix** — contrast against each bundled theme,
  reduced-motion, zoom, and overlay clipping

Run both for any change that touches overlay or keyboard behaviour. The
matrix is the source of truth for “does Sketchy still have contrast on
`btn-outline-secondary`”, not a screenshot in a pull request description.

## Testing

Practical sequence:

1. Unplug the mouse. Reach every control with Tab / Shift+Tab. Open and
   close Modal, Offcanvas, DropdownMenu, Tabs, and Accordion using only
   the keys above.
2. Confirm focus restore: the opener is focused after close, not `body`.
3. Confirm the one-modal policy by attempting to open a second Modal.
4. Run axe (or an equivalent WCAG checker) on a mixed page: NiceGUI chrome
   plus a `bs.scope()` island. Fix violations in *your* markup first
   (`aria-label` on icon-only buttons, labels for inputs).
5. Repeat on a dark theme (`DARKLY` or `data-bs-theme="dark"`) because
   contrast failures cluster there.

axe cannot hear a focus trap. Keyboard-only testing is not optional.

Icon-only controls need an accessible name; see [Icons](../icons.md).
Mixed-mode CSS must not hide Quasar focus rings or Bootstrap `:focus-visible`
outlines in `@layer overrides`. If you restyle focus, restyle both.

See also [FAQ](../faq.md) and
[Mixing with NiceGUI pages](mixed-nicegui-pages.md).
