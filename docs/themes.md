# Themes and icons

`setup()` uses the bundled Bootstrap stylesheet by default. The catalogue also
includes `GRID` and these Bootswatch 5.3.8 themes:

`CERULEAN`, `COSMO`, `CYBORG`, `DARKLY`, `FLATLY`, `JOURNAL`, `LITERA`,
`LUMEN`, `LUX`, `MATERIA`, `MINTY`, `MORPH`, `PULSE`, `QUARTZ`, `SANDSTONE`,
`SIMPLEX`, `SKETCHY`, `SLATE`, `SOLAR`, `SPACELAB`, `SUPERHERO`, `UNITED`,
`VAPOR`, `YETI`, and `ZEPHYR`.

Pass a constant or its lowercase name:

```python
from nicegui_bootstrap_components import setup, themes

setup(theme=themes.FLATLY)
# The lowercase name is equivalent in a separate setup call.
# setup(theme="flatly")
```

Icon stylesheets are optional. Bootstrap Icons 1.11.3 and Font Awesome 6.7.2
are bundled with their referenced font files:

```python
from nicegui_bootstrap_components import icons, setup

setup(icons=icons.BOOTSTRAP)
setup(icons="fontawesome")
```

Use `cdn=True` only with an unscoped style mode for theme CSS. Requested icon
styles use their pinned jsDelivr URLs when CDN mode is enabled.
