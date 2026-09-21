# Quickstart

Install the package, render a first component, choose a style mode, and apply a
theme. Process-level asset options live on `setup`; per-client theme and
color-mode switches go through `ThemeController.for_client()`.

!!! note
    The public API is modelled on dash-bootstrap-components 2.0.4. Dash-specific
    features such as callbacks and persistence are adapted for NiceGUI. Each
    component page records supported, adapted, and excluded props.

## Install

Requires Python 3.10 or later. Install from PyPI:

```bash
pip install nicegui-bootstrap-components
```

The library targets NiceGUI 3.17.1 and Bootstrap 5.3.8.

## Your first app

Create a module, wrap Bootstrap widgets in `bs.scope()`, and start NiceGUI:

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    bs.button("Hello", color="primary")

ui.run()
```

`bs.button` is the native surface. The compatibility surface (`dbc`) follows the
same component set with dash-bootstrap-components prop names.

## Style modes

**Scoped.** `with bs.scope():` marks a Bootstrap island. Styles apply inside
that subtree, which is the recommended pattern on pages that also use NiceGUI
defaults.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

ui.label("NiceGUI chrome outside the island")
with bs.scope():
    bs.button("Scoped button", color="primary")
```

**Unscoped.** Components created outside a scope still render, but Bootstrap
then shares the page with NiceGUI's unlayered CSS. Typography, reboot rules, and
spacing can leak. Prefer `bs.scope()` on mixed pages.

## Themes

Theme and color-mode choices are per client. Inside a page, call
`ThemeController.for_client()` and switch the stylesheet or the color mode
from there:

```python
from nicegui import ui
from nicegui_bootstrap_components import ThemeController, bs

@ui.page("/")
def index() -> None:
    controller = ThemeController.for_client()
    controller.set_theme("flatly")
    controller.set_color_mode("dark")

    with bs.scope():
        bs.button("Themed button", color="primary")

ui.run()
```

For process-level defaults (applied before any client connects), pass
`theme=` and `color_mode=` to `setup()`. Twenty-five Bootswatch themes are
available. Switching at runtime keeps each connected client on its own
choice; other clients keep the sheet they already have.
