# Modal

`Modal` is Bootstrap 5's dialog overlay: a titled panel that sits above the
page for confirmation, short forms, or detail the user did not ask to navigate
away for. The family is `Modal`, `ModalHeader`, `ModalTitle`, `ModalBody`, and
`ModalFooter`. The dialog is rendered through an overlay portal so z-index and
positioning stay above the rest of the layout.

## Basic usage

Build the sections in order: header (with title), body, footer. Keep the
default backdrop and keyboard behavior unless you have a reason to lock the
dialog.

{{example:examples/components/modal/confirm_publish.py:demo}}

## Live example

The snippet below is exactly what the demo service runs. The highlighted
`demo()` function is the same source the demo executes, not a rewritten copy.

{{example:examples/components/modal/static_backdrop.py:demo}}

## Options

### size

`size` is the Bootstrap dialog width token. Use `"sm"` for short confirms,
omit it for the default, `"lg"` for a small form, and `"xl"` when the body
holds a table or a two-column layout. Size does not change header or footer
structure.

### backdrop

`backdrop=False` removes the dimmed layer behind the dialog. The overlay
portal still hosts the modal, but the page is not shaded. A static backdrop
(the Bootstrap `static` value) keeps the shade and ignores clicks on it, so
the user cannot dismiss by clicking outside. Pair a static backdrop with an
explicit close button in the header or footer.

### keyboard and Escape

`keyboard` controls whether the Escape key dismisses the dialog. With a static
backdrop, Escape still closes the modal when `keyboard` is true; set
`keyboard` to false when the user must choose an on-dialog action (for
example a blocking confirm). `backdrop=False` does not by itself disable
Escape — that is `keyboard`.

### Family roles

- `Modal` is the overlay host. It owns `backdrop`, `keyboard`, and `size`.
- `ModalHeader` is the top bar; put `ModalTitle` inside it, not beside it.
- `ModalTitle` is the accessible name of the dialog.
- `ModalBody` is the scrollable content slot.
- `ModalFooter` holds dismissing and confirming actions.

Do not skip the title if the body is a form: screen readers use it as the
dialog name. The portal keeps the markup out of local stacking contexts, which
is why a modal inside a transformed card still covers the page.

## Notes

Footer buttons use NiceGUI `on_click` callables. There is no modal-level
`n_clicks`; count or handle clicks on the `Button` components you place in the
header and footer.

## Argument reference

{{apidoc:Modal}}
