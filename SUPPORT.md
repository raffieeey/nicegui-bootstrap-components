# Support Matrix

The library exposes two import surfaces: `bs` (native) and `dbc` (compat with
dash-bootstrap-components 2.0.4). The table below is the authoritative status
for each component on both surfaces.

| Component | Family | Native (bs) | Compat (dbc) | Notes |
| --- | --- | --- | --- | --- |
| Accordion | Accordion | supported | supported | adapted semantics |
| AccordionItem | Accordion | supported | supported | adapted semantics |
| Alert | Alert | supported | supported | |
| Badge | Badge | supported | supported | |
| Breadcrumb | Breadcrumb | supported | supported | |
| Button | Button | supported | supported | adapted semantics; `external_link` only when rendered as an anchor |
| ButtonGroup | Button | supported | supported | |
| Card | Card | supported | supported | |
| CardBody | Card | supported | supported | |
| CardFooter | Card | supported | supported | |
| CardGroup | Card | supported | supported | |
| CardHeader | Card | supported | supported | |
| CardImg | Card | supported | supported | |
| CardImgOverlay | Card | supported | supported | |
| CardLink | Card | supported | supported | adapted semantics |
| Carousel | Carousel | supported | supported | `ride` removed |
| Checkbox | Form | supported | supported | adapted semantics |
| Checklist | Form | supported | supported | adapted semantics |
| Col | Layout | supported | supported | |
| Collapse | Collapse | supported | supported | |
| Container | Layout | supported | supported | |
| DropdownMenu | Dropdown | supported | supported | `is_open` is native-only |
| DropdownMenuItem | Dropdown | supported | supported | adapted semantics |
| Fade | Fade | supported | supported | `is_in` only |
| Form | Form | supported | supported | |
| FormFeedback | Form | supported | supported | |
| FormFloating | Form | supported | supported | |
| FormText | Form | supported | supported | |
| Input | Form | supported | supported | adapted semantics; `type="color"` and `debounce` are native-only |
| InputGroup | Form | supported | supported | |
| InputGroupText | Form | supported | supported | |
| Label | Form | supported | supported | |
| ListGroup | List group | supported | supported | |
| ListGroupItem | List group | supported | supported | |
| Modal | Modal | supported | supported | |
| ModalBody | Modal | supported | supported | |
| ModalFooter | Modal | supported | supported | |
| ModalHeader | Modal | supported | supported | |
| ModalTitle | Modal | supported | supported | |
| Nav | Nav | supported | supported | |
| Navbar | Navbar | supported | supported | `light` removed |
| NavbarBrand | Navbar | supported | supported | adapted semantics |
| NavbarSimple | Navbar | supported | supported | adapted semantics |
| NavbarToggler | Navbar | supported | supported | |
| NavItem | Nav | supported | supported | |
| NavLink | Nav | supported | supported | adapted semantics |
| Offcanvas | Offcanvas | supported | supported | |
| Pagination | Pagination | supported | supported | |
| Placeholder | Placeholder | supported | supported | adapted semantics |
| Popover | Popover | supported | supported | |
| PopoverBody | Popover | supported | supported | |
| PopoverHeader | Popover | supported | supported | |
| Progress | Progress | supported | supported | |
| RadioButton | Form | supported | supported | adapted semantics |
| RadioItems | Form | supported | supported | adapted semantics |
| Row | Layout | supported | supported | |
| Scope | Layout | supported | not applicable | native-only; marks a scoped island |
| Select | Form | supported | supported | adapted semantics |
| Spinner | Spinner | supported | supported | adapted semantics |
| Stack | Layout | supported | supported | |
| Switch | Form | supported | supported | adapted semantics |
| Tab | Tabs | supported | supported | adapted semantics |
| Table | Table | supported | supported | compat `from_dataframe` defaults `index=True` |
| Tabs | Tabs | supported | supported | adapted semantics |
| Textarea | Form | supported | supported | adapted semantics |
| Toast | Toast | supported | supported | |
| Tooltip | Tooltip | supported | supported | |

## Adapted semantics

- Persistence analogue: `persist="local|session"` requires a public `id`.
- Navigation analogue: internal versus external link policy (for example
  `external_link` on Button applies only when the control is rendered as an
  anchor).
- Loading analogue: an explicit `loading` prop rather than a Dash loading
  wrapper.
- Dash callbacks and pattern-matching IDs are excluded; use NiceGUI handlers.
