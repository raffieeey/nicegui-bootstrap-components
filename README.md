# nicegui-bootstrap-components

Bootstrap 5 components for [NiceGUI](https://nicegui.io). The public API matches
the [dash-bootstrap-components](https://github.com/facultyai/dash-bootstrap-components)
2.0.4 API for the component set listed below.

[![CI](https://github.com/raffieeey/nicegui-bootstrap-components/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/raffieeey/nicegui-bootstrap-components/actions/workflows/ci.yml)
[![Python >=3.10](https://img.shields.io/badge/python-%3E%3D3.10-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Install

The package requires Python 3.10 or later and NiceGUI >=3.17.1,<4; it has been
tested against NiceGUI 3.17.1. It bundles Bootstrap 5.3.8. CI checks the oldest
supported NiceGUI release and the newest available 3.x release.

```bash
pip install nicegui-bootstrap-components
```

`Table.from_dataframe` needs pandas, installed by the optional extra:

```bash
pip install "nicegui-bootstrap-components[examples]"
```

## Quickstart

Save this as `app.py` and run `python app.py`. Open the local URL printed in the
terminal.

```python
from nicegui import ui
from nicegui_bootstrap_components import bs

with bs.scope(), bs.container():
    with bs.row():
        with bs.col(width=12, md=6):
            bs.input(placeholder="Name")
            bs.button("Save", color="primary", on_click=lambda: ui.notify("Saved"))

ui.run()
```

## Two API surfaces

`nicegui_bootstrap_components.bs` is the native surface: 67 PascalCase classes
and 67 snake_case aliases (134 exports). Use it for new NiceGUI code.

`nicegui_bootstrap_components.dbc` is the compatibility surface (66 exports)
with dash-bootstrap-components 2.0.4 prop names. Use it when porting Dash layouts.

```python
from nicegui import ui
from nicegui_bootstrap_components import dbc

dbc.Container(
    dbc.Row(dbc.Col(dbc.Button("Save", color="primary"), md=6)),
    fluid=True,
)
```

Top-level exports: `StyleMode`, `ThemeController`, `bs`, `dbc`, `icons`, `setup`,
`themes`, `__version__`.

## Style modes

`setup()` registers library CSS once, process-wide, and is idempotent for the same
arguments. A conflicting mode, or scoped mode with `cdn=True`, raises `ValueError`.

- `StyleMode.UNSCOPED` (`"unscoped"`): Bootstrap-first page.
- `StyleMode.MIXED` (`"mixed"`): scoped Bootstrap islands inside an existing
  NiceGUI/Quasar page. Mark islands with `bs.scope()` (`bs.Scope` is the class form).

```python
from nicegui_bootstrap_components import StyleMode, setup, themes

setup(mode=StyleMode.MIXED, theme=themes.FLATLY, color_mode="auto")
```

## Themes and dark mode

27 constants on `themes`: Bootstrap itself, the grid-only build, and 25 Bootswatch
themes. `color_mode="auto"` follows the host app. Pass `icons.BOOTSTRAP` or
`icons.FONT_AWESOME` to `setup(icons=...)`.

`BOOTSTRAP`, `CERULEAN`, `COSMO`, `CYBORG`, `DARKLY`, `FLATLY`, `GRID`, `JOURNAL`,
`LITERA`, `LUMEN`, `LUX`, `MATERIA`, `MINTY`, `MORPH`, `PULSE`, `QUARTZ`, `SANDSTONE`,
`SIMPLEX`, `SKETCHY`, `SLATE`, `SOLAR`, `SPACELAB`, `SUPERHERO`, `UNITED`, `VAPOR`,
`YETI`, `ZEPHYR`.

## Components

67 native names (each has a snake_case alias on `bs`):

Accordion, AccordionItem, Alert, Badge, Breadcrumb, Button, ButtonGroup, Card, CardBody,
CardFooter, CardGroup, CardHeader, CardImg, CardImgOverlay, CardLink, Carousel, Checkbox,
Checklist, Col, Collapse, Container, DropdownMenu, DropdownMenuItem, Fade, Form,
FormFeedback, FormFloating, FormText, Input, InputGroup, InputGroupText, Label, ListGroup,
ListGroupItem, Modal, ModalBody, ModalFooter, ModalHeader, ModalTitle, Nav, NavItem,
NavLink, Navbar, NavbarBrand, NavbarSimple, NavbarToggler, Offcanvas, Pagination,
Placeholder, Popover, PopoverBody, PopoverHeader, Progress, RadioButton, RadioItems, Row,
Scope, Select, Spinner, Stack, Switch, Tab, Table, Tabs, Textarea, Toast, Tooltip.

## Layout

```python
from nicegui_bootstrap_components import bs

with bs.scope(), bs.container():
    with bs.row():
        with bs.col(width=12, md=4):
            bs.label("Full width on phones, one third from md")
        with bs.col(width=12, md=4):
            bs.label("Middle")
        with bs.col(width=12, md=4):
            bs.label("Right")
```

## Forms

```python
from nicegui_bootstrap_components import bs

with bs.scope():
    bs.input(placeholder="Your name", on_change=lambda: None)
    bs.select(options={"my": "Malaysia", "sg": "Singapore"}, value="my")
    bs.checkbox(label="Remember me")
    bs.switch(label="Enable alerts")
```

## Cards, alerts, and badges

```python
from nicegui_bootstrap_components import bs

with bs.scope(), bs.card():
    bs.card_header("Header")
    with bs.card_body():
        bs.alert("Something happened.", color="info", dismissable=True)
        bs.badge("New", color="success")
```

## Modal

```python
from nicegui_bootstrap_components import bs

with bs.scope():
    with bs.modal() as modal:
        bs.modal_header("Title")
        bs.modal_body("Content")
        bs.modal_footer(bs.button("Close", on_click=modal.close))
```

## Table

```python
import pandas as pd
from nicegui_bootstrap_components import bs

df = pd.DataFrame({"city": ["Kuala Lumpur"], "country": ["Malaysia"]})

with bs.scope():
    bs.Table.from_dataframe(df, striped=True, bordered=False, hover=True)
```

## Examples

The gallery mirrors dash-bootstrap-components: Layer 1 component examples, Layer 2
composite apps (Iris, Graphs in Tabs, Simple Sidebar), and Layer 3 templates.

## Documentation

[https://github.com/raffieeey/nicegui-bootstrap-components](https://github.com/raffieeey/nicegui-bootstrap-components)

## Development

```bash
git clone https://github.com/raffieeey/nicegui-bootstrap-components.git
cd nicegui-bootstrap-components
pip install -e ".[dev]"
pytest
```

`python -m playwright install chromium`. At 0.1.0, the default run carries
545 tests plus the Playwright browser suite and the visual matrix; mypy and
ruff are clean. CI runs three GitHub Actions jobs (checks, docs, browser). The
browser suite uses real Chromium. Every Python block in the docs and every
example is executed by tests, so a snippet that cannot run fails CI.

## License

MIT. See [LICENSE](LICENSE).

## Status

0.1.0. Matches the dash-bootstrap-components 2.0.4 API for the component set listed
above. Not yet on PyPI.
