"""Native ``bs.scope`` island wrapper (Mode B Reboot / selector anchor)."""

from __future__ import annotations

from typing import Any

from .._base import BootstrapElement

__all__ = ["Scope", "scope"]


class Scope(BootstrapElement):
    """Mode B island / Reboot scope-anchor. Tag ``div``, class ``ngbs``.

    Individual components do not carry ``ngbs``; Bootstrap selectors are rewritten
    against this ancestor (and the overlay root).
    """

    component_name = "Scope"
    children_kind = "auto"

    def __init__(self, children: object = None, **props: Any) -> None:
        self._surface = "native"
        self._structural_classes = ("ngbs",)
        super().__init__(children, tag="div", **props)


scope = Scope
