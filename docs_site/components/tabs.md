# Tabs

Tabs switch between peer panels of content in the same region. They map to Bootstrap
5 tabbed navigation (`nav-tabs` / `nav-pills`) and are the usual pattern for
settings pages, item inspectors, and any view where the user flips between a small
set of named sections.

Use Tabs when every panel is equally important and should stay mounted in the page.
Use an Offcanvas or a separate route when a section is a destination of its own.

## Basic usage

{{example:examples/components/tabs/basic_usage.py:demo}}

Compose `Tabs` with `Tab` children. Each `Tab` holds the panel body for that
section. `active_tab` selects which panel is shown first; `on_change` runs when the
user picks another tab.

## Live example

The snippets below are exactly what the demo service runs. Each highlighted
`demo()` function is the same source the demo executes, not a rewritten copy.

### Card tabs

{{example:examples/components/tabs/card_tabs.py:demo}}

### Tabs without ids

{{example:examples/components/tabs/no_ids.py:demo}}

## Options

### Composition

Pass every panel as a `Tab` child of `Tabs`. The tab label and the panel content
come from that child. Keep the number of tabs small; a long row of labels is harder
to scan than a vertical nav.

{{example:examples/components/tabs/composition.py:demo}}

Put structured widgets inside each `Tab` when the panel is more than a sentence.
The tab strip stays the navigation; the child is the page.

### Active tab and on_change

`active_tab` is the identifier of the selected panel. Keep it in application state
so deep links, breadcrumbs, and the tab strip all agree. `on_change` is the Python
handler for a user-driven switch: persist the choice, lazy-load the panel, or sync
a URL parameter.

{{example:examples/components/tabs/active_tab_on_change.py:demo}}

Do not rebuild the whole `Tabs` tree just to change the selection; update
`active_tab` and let the component restyle the strip.

### Pills and card

`class_name="nav-pills"` switches the strip to Bootstrap's pill style instead of
underlined tabs. That style sits well on tinted headers and compact toolbars.
`card` wraps the strip and panels in a card-like frame so the tabs read as one
surface, which is useful on dashboards where the control is a standalone block.

{{example:examples/components/tabs/with_card.py:demo}}

Pill styling and card compose: `nav-pills` changes the labels, card changes the chrome. Use one
or both, but keep the choice consistent across the app so tab strips do not look
like different components.

## Argument reference

{{apidoc:Tabs}}
