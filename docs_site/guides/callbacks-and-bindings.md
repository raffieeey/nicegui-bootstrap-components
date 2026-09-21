# Callbacks and bindings

dash-bootstrap-components sits on Dash’s callback graph: `Input`, `Output`,
`State`, and pattern-matching IDs. This library sits on NiceGUI: Python
handlers registered in constructors, `ValueElement.value`, `on_change`, and
`bind_value`. Visual props port. The event model does not.

There is no `@callback`. There is no hidden `n_clicks` Input. A click is a
function you passed to `on_click`. A typed value is `element.value` or a
binding to an object attribute.

## Two event models

Dash collects ids, waits for a trigger, and calls one function with every
Input/State in the signature. NiceGUI calls the handler you registered on
that element. The handler already closes over the widgets it needs.

Consequences:

- You mutate other elements directly (`label.set_text(...)`) instead of
  returning a dict of outputs.
- Local Python variables (or a small state object) replace `dcc.Store` for
  in-page state.
- Handlers run in the UI process. Long work belongs in `asyncio` tasks or
  a worker queue, not in the click handler.
- Pattern-matching IDs (`ALL`, `MATCH`, `ALLSMALLER`) are not ported. See
  [What is not ported](#what-is-not-ported).

The `dbc` compat surface keeps Dash *prop names* where they are portable
(`color=`, `outline=`, `active_tab=`). It does not keep Dash *callbacks*.

## Click handlers

Register `on_click` on `Button`. The listener is attached in `__init__`
only. A small page that mutates a `ui.label`:

```python
from nicegui import ui
from nicegui_bootstrap_components import bs
from nicegui_bootstrap_components.assets import setup

setup(mode="mixed")

@ui.page("/")
def page() -> None:
    clicks = {"n": 0}
    label = ui.label("Clicked 0 times")

    def on_click() -> None:
        clicks["n"] += 1
        label.set_text(f"Clicked {clicks['n']} times")

    with bs.scope():
        bs.button("Click me", color="primary", on_click=on_click)
```

The dict is a mutable cell so the nested function can update it without
`nonlocal`. A dataclass or a one-field namespace works the same way.
`label` is a NiceGUI widget; mixing `ui.label` outside `bs.scope()` with a
Bootstrap button inside it is the intended hybrid pattern (see
[Mixing with NiceGUI pages](mixed-nicegui-pages.md)).

Other click-like components follow the same rule: pass `on_click` (or the
component’s documented handler name) into the constructor. Do not attach
class-level listeners, and do not re-bind on every click.

## Local counters, not Dash `n_clicks`

In Dash, `n_clicks` is an Input. Callbacks fire when it changes, and
`prevent_initial_call` is how you skip the first run. In this library a
click counter is local state.

Keep the integer in Python, as in the example above. If a component accepts
an initial `n_clicks=` value, that is a starting count for that instance,
not a graph Input. Do not write a handler that “waits for n_clicks to
change”; write `on_click`.

Because the counter is local:

- Reloading the page resets it unless you also persist something else.
- Two buttons do not share a count unless you close over the same cell.
- Tests assert on the label (or on your state object), not on a Dash
  `callback_context`.

## `on_change` and `bind_value`

Value-carrying controls (`BootstrapValueElement`: inputs, checkboxes, tabs,
and similar) expose `.value`, `on_change`, and `bind_value`. The frontend
contract is the `model-value` prop and the `update:modelValue` event.
Loopback protection is in the base class; a programmatic `.value = ...`
does not re-enter your handler.

Handler plus binding against a small state object:

```python
from nicegui import ui
from nicegui_bootstrap_components import bs
from nicegui_bootstrap_components.assets import setup

setup(mode="mixed")

class FormState:
    name: str = ""

@ui.page("/")
def page() -> None:
    state = FormState()
    status = ui.label("")

    def on_change() -> None:
        status.set_text(f"name is {state.name!r}")

    with bs.scope():
        field = bs.input(on_change=on_change)
    field.bind_value(state, "name")
    ui.label().bind_text_from(state, "name")
```

`bind_value` keeps `state.name` and the control in sync. `bind_text_from`
(NiceGUI) mirrors that value onto a label. You can use a handler, a
binding, or both; restoration from `persist=` does **not** fire `on_change`
(see [Compatibility](../compatibility.md)).

Not every Bootstrap component is a value control. Structural pieces
(`Card`, `Row`, `Navbar`) have no `.value`. Check the component page when
unsure.

## Tabs

`Tabs` is a value-carrying control: `.value` is the active tab, and
`on_change` runs when the user (or your code) changes it.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs
from nicegui_bootstrap_components.assets import setup

setup(mode="mixed")

@ui.page("/")
def page() -> None:
    label = ui.label("no tab yet")
    tabs = None

    def on_tab_change() -> None:
        if tabs is not None:
            label.set_text(f"active tab: {tabs.value}")

    with bs.scope():
        tabs = bs.tabs(on_change=on_tab_change)
```

Read `tabs.value` inside the handler rather than parsing a Dash
`callback_context`. If you need the previous tab, store it yourself; the
library does not keep a hidden `prev_active_tab` Input.

Keyboard behaviour for tabs is in [Accessibility](accessibility.md).

## What is not ported

Pattern-matching IDs are excluded. There is no `ALL`, `MATCH`, or
`ALLSMALLER`. If you generated a grid of Dash inputs with a matched id
dict, build the widgets in a Python loop and close over each instance:

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

@ui.page("/")
def page() -> None:
    labels = []
    with bs.scope():
        for index in range(3):
            label = ui.label(f"row {index}: 0")
            labels.append(label)

            def make_handler(i: int):
                def on_click() -> None:
                    labels[i].set_text(f"row {i}: clicked")

                return on_click

            bs.button(f"Row {index}", on_click=make_handler(index))
```

Factory functions (as above) avoid the late-binding loop gotcha. Dash
clientside callbacks, `dash.no_update`, and `callback_context.triggered_id`
have no equivalents; branch in ordinary Python instead.

## Persistence

`persist="local"` or `persist="session"` plus a public `id` stores the
control’s value across reloads. Restore does not fire `on_change`, so a
binding updates and your handler does not. That is intentional: a reload
should not look like a user edit. Details are in
[Compatibility](../compatibility.md) and [FAQ](../faq.md).

See also [Mixing with NiceGUI pages](mixed-nicegui-pages.md).
