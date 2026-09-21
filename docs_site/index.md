# NiceGUI Bootstrap Components

NiceGUI Bootstrap Components is a Bootstrap 5.3 component library for NiceGUI.
The public API is modelled on dash-bootstrap-components 2.0.4, with a native
`bs` surface and a `dbc` compatibility surface.

## Features

- 66 components
- 25 Bootswatch themes
- Bootstrap Icons
- Light and dark color modes
- Scoped and unscoped style modes

## Install

```bash
pip install nicegui-bootstrap-components
```

## First app

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope():
    bs.button("Hello", color="primary")

ui.run()
```

See the [Quickstart](quickstart.md) for style modes, themes, and a complete
runnable example.
