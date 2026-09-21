"""Selectable stylesheet constants and their pinned CDN twins."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "BOOTSTRAP",
    "GRID",
    "CERULEAN",
    "COSMO",
    "CYBORG",
    "DARKLY",
    "FLATLY",
    "JOURNAL",
    "LITERA",
    "LUMEN",
    "LUX",
    "MATERIA",
    "MINTY",
    "MORPH",
    "PULSE",
    "QUARTZ",
    "SANDSTONE",
    "SIMPLEX",
    "SKETCHY",
    "SLATE",
    "SOLAR",
    "SPACELAB",
    "SUPERHERO",
    "UNITED",
    "VAPOR",
    "YETI",
    "ZEPHYR",
    "Theme",
]

_CDN_ROOT = "https://cdn.jsdelivr.net/npm"
_BOOTSTRAP_VERSION = "5.3.8"


@dataclass(frozen=True)
class Theme:
    """One selectable stylesheet: a bundled build plus its pinned CDN twin.

    ``bundled`` names the package stylesheet pair: ``<bundled>.css`` is the
    scoped build and ``<bundled>-unscoped.css`` applies document-wide.
    """

    name: str
    cdn: str
    bundled: str


BOOTSTRAP = Theme(
    name="bootstrap",
    cdn=f"{_CDN_ROOT}/bootstrap@{_BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css",
    bundled="ngbs-bootstrap",
)

GRID = Theme(
    name="grid",
    cdn=f"{_CDN_ROOT}/bootstrap@{_BOOTSTRAP_VERSION}/dist/css/bootstrap-grid.min.css",
    bundled="ngbs-grid",
)


def _bootswatch(name: str) -> Theme:
    return Theme(
        name=name,
        cdn=f"{_CDN_ROOT}/bootswatch@{_BOOTSTRAP_VERSION}/dist/{name}/bootstrap.min.css",
        bundled=f"ngbs-{name}",
    )


CERULEAN = _bootswatch("cerulean")
COSMO = _bootswatch("cosmo")
CYBORG = _bootswatch("cyborg")
DARKLY = _bootswatch("darkly")
FLATLY = _bootswatch("flatly")
JOURNAL = _bootswatch("journal")
LITERA = _bootswatch("litera")
LUMEN = _bootswatch("lumen")
LUX = _bootswatch("lux")
MATERIA = _bootswatch("materia")
MINTY = _bootswatch("minty")
MORPH = _bootswatch("morph")
PULSE = _bootswatch("pulse")
QUARTZ = _bootswatch("quartz")
SANDSTONE = _bootswatch("sandstone")
SIMPLEX = _bootswatch("simplex")
SKETCHY = _bootswatch("sketchy")
SLATE = _bootswatch("slate")
SOLAR = _bootswatch("solar")
SPACELAB = _bootswatch("spacelab")
SUPERHERO = _bootswatch("superhero")
UNITED = _bootswatch("united")
VAPOR = _bootswatch("vapor")
YETI = _bootswatch("yeti")
ZEPHYR = _bootswatch("zephyr")


_CATALOGUE = (
    BOOTSTRAP,
    GRID,
    CERULEAN,
    COSMO,
    CYBORG,
    DARKLY,
    FLATLY,
    JOURNAL,
    LITERA,
    LUMEN,
    LUX,
    MATERIA,
    MINTY,
    MORPH,
    PULSE,
    QUARTZ,
    SANDSTONE,
    SIMPLEX,
    SKETCHY,
    SLATE,
    SOLAR,
    SPACELAB,
    SUPERHERO,
    UNITED,
    VAPOR,
    YETI,
    ZEPHYR,
)
