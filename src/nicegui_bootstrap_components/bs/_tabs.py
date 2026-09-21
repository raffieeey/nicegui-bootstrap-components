"""Tabs family: Tabs and Tab."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import partial
from typing import Any

from nicegui import ui
from nicegui.element import Element

from .._base import (
    BootstrapElement,
    ChildrenError,
    UnsupportedPropError,
    make_surface_classes,
    normalize_style,
    resolve_class_name,
)

__all__ = [
    "Tabs",
    "DbcTabs",
    "tabs",
    "Tab",
    "DbcTab",
    "tab",
    "assign_tab_ids",
    "first_enabled_tab_id",
    "tab_button_aria",
    "tab_link_classes",
    "tab_pane_aria",
    "tab_pane_classes",
    "tabs_card_body_classes",
    "tabs_card_header_classes",
    "tabs_content_classes",
    "tabs_nav_classes",
    "tabs_nav_item_classes",
    "tabs_structural_classes",
]

_PERSIST_VALUES = ("off", "local", "session", "memory")
_ACTIVE_TAB_MEMORY: dict[str, str] = {}

_TABLIST_KEYDOWN = """(e) => {
  const key = e.key;
  if (key !== 'ArrowLeft' && key !== 'ArrowRight' && key !== 'Home' && key !== 'End') return;
  const root = e.currentTarget;
  if (!root || !root.querySelectorAll) return;
  const tabs = Array.from(root.querySelectorAll('[role="tab"]')).filter((el) => {
    return !el.disabled && el.getAttribute('aria-disabled') !== 'true'
      && !el.classList.contains('disabled');
  });
  if (!tabs.length) return;
  let idx = tabs.indexOf(document.activeElement);
  if (key === 'Home') idx = 0;
  else if (key === 'End') idx = tabs.length - 1;
  else if (key === 'ArrowLeft') idx = idx <= 0 ? tabs.length - 1 : idx - 1;
  else if (key === 'ArrowRight') idx = (idx + 1) % tabs.length;
  e.preventDefault();
  const next = tabs[idx];
  if (next) { next.focus(); next.click(); }
}"""


def tabs_structural_classes(*, card: bool = False) -> list[str]:
    """Return structural classes for the Tabs root."""
    if card:
        return ["card"]
    return []


def tabs_nav_classes(*, card: bool = False) -> list[str]:
    """Return Bootstrap ``nav nav-tabs`` classes, with card-header-tabs when card."""
    classes = ["nav", "nav-tabs"]
    if card:
        classes.append("card-header-tabs")
    return classes


def tabs_nav_item_classes() -> list[str]:
    """Return Bootstrap classes for a tab list item."""
    return ["nav-item"]


def tabs_card_header_classes() -> list[str]:
    """Return Bootstrap card header classes for card tabs."""
    return ["card-header"]


def tabs_card_body_classes() -> list[str]:
    """Return Bootstrap card body classes for card tabs."""
    return ["card-body"]


def tabs_content_classes() -> list[str]:
    """Return Bootstrap tab content wrapper classes."""
    return ["tab-content"]


def tab_link_classes(*, active: bool = False, disabled: bool = False) -> list[str]:
    """Return Bootstrap ``nav-link`` classes for a tab button."""
    classes = ["nav-link"]
    if active:
        classes.append("active")
    if disabled:
        classes.append("disabled")
    return classes


def tab_pane_classes(*, active: bool = False) -> list[str]:
    """Return Bootstrap ``tab-pane`` classes."""
    classes = ["tab-pane"]
    if active:
        classes.append("active")
    return classes


def assign_tab_ids(tab_ids: Sequence[str | None]) -> list[str]:
    """Return stable tab ids for the given child order.

    Missing ids become ``tab-0``, ``tab-1``, ... using the child index when free,
    then the lowest unused ``tab-n`` if that index collides with an explicit id.
    Existing ids are preserved.
    """
    used = {item for item in tab_ids if item}
    result: list[str] = []
    for index, current in enumerate(tab_ids):
        if current:
            result.append(current)
            continue
        candidate = f"tab-{index}"
        if candidate in used:
            n = 0
            while f"tab-{n}" in used:
                n += 1
            candidate = f"tab-{n}"
        used.add(candidate)
        result.append(candidate)
    return result


def first_enabled_tab_id(tab_ids: Sequence[str], disabled: Sequence[bool]) -> str | None:
    """Return the first tab id whose matching disabled flag is false."""
    for tab_id, is_disabled in zip(tab_ids, disabled, strict=True):
        if not is_disabled:
            return tab_id
    return None


def tab_button_aria(
    *,
    tab_id: str,
    pane_id: str,
    selected: bool,
    disabled: bool = False,
) -> dict[str, str]:
    """Return ARIA attributes for a tab button."""
    attrs = {
        "role": "tab",
        "id": f"{tab_id}-tab",
        "aria-controls": pane_id,
        "aria-selected": "true" if selected else "false",
        "tabindex": "0" if selected and not disabled else "-1",
    }
    if disabled:
        attrs["aria-disabled"] = "true"
    return attrs


def tab_pane_aria(*, tab_id: str, pane_id: str, selected: bool) -> dict[str, str]:
    """Return ARIA attributes for a tab pane."""
    return {
        "role": "tabpanel",
        "id": pane_id,
        "aria-labelledby": f"{tab_id}-tab",
        "aria-hidden": "false" if selected else "true",
    }


def _is_tab_element(value: object) -> bool:
    return getattr(type(value), "component_name", None) == "Tab"


def _element_children(element: Any) -> list[Any]:
    slot = getattr(element, "default_slot", None)
    if slot is None:
        return []
    children = getattr(slot, "children", None)
    if not children:
        return []
    return list(children)


def _coerce_tab_children(children: object) -> list[Any]:
    if children is None:
        return []
    if _is_tab_element(children):
        return [children]
    if isinstance(children, (str, bytes, bytearray)):
        raise ChildrenError("Tabs does not accept text children; wrap text in a Tab component.")
    if isinstance(children, Sequence):
        items = list(children)
    else:
        raise ChildrenError(
            "Tabs only accepts Tab children; wrap other content in a Tab component."
        )
    result: list[Any] = []
    for child in items:
        if isinstance(child, str):
            raise ChildrenError("Tabs does not accept text children; wrap text in a Tab component.")
        if not _is_tab_element(child):
            raise ChildrenError(
                "Tabs only accepts Tab children; wrap other content in a Tab component."
            )
        result.append(child)
    return result


def _set_class(element: Any, name: str, present: bool) -> None:
    if present:
        element.classes(add=name)
    else:
        element.classes(remove=name)


def _apply_style(element: Any, style: dict[str, Any] | str | None) -> None:
    if style is None:
        return
    if isinstance(style, dict):
        element.style(normalize_style(style))
        return
    element.style(str(style))


def _pane_dom_id(tab: Any) -> str:
    current = tab._props.get("id")
    if isinstance(current, str) and current:
        return current
    assigned = tab.tab_id or "tab"
    tab._props["id"] = assigned
    return assigned


class _TabImpl(BootstrapElement):
    """Private Tab implementation. Renders as a pane; the parent Tabs owns the tab button."""

    component_name = "Tab"
    children_kind = "auto"
    reserved_classes = ("tab-pane",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        label: str | None = None,
        tab_id: str | None = None,
        disabled: bool = False,
        label_class_name: str | None = None,
        label_style: dict[str, Any] | str | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        label_class_alias = kwargs.pop("labelClassName", None)
        self._label_class_name = resolve_class_name(
            label_class_name, label_class_alias, self._surface
        )
        tab_class_name = kwargs.pop("tab_class_name", None)
        tab_class_alias = kwargs.pop("tabClassName", None)
        self._tab_class_name = resolve_class_name(tab_class_name, tab_class_alias, self._surface)
        self._tab_style = kwargs.pop("tab_style", None)
        kwargs.pop("tabStyle", None)
        for extra in (
            "key",
            "loading_state",
            "active_label_style",
            "active_label_class_name",
            "active_labelClassName",
            "active_tab_class_name",
            "active_tab_style",
            "active_tabClassName",
            "active_tab_className",
        ):
            kwargs.pop(extra, None)
        self._label = label
        self._explicit_tab_id = tab_id if tab_id else None
        self._tab_id = self._explicit_tab_id
        self._disabled = bool(disabled)
        self._label_style = label_style
        self._structural_classes = tuple(tab_pane_classes(active=False))
        super().__init__(children, tag="div", **kwargs)
        self._props["role"] = "tabpanel"

    @property
    def tab_id(self) -> str | None:
        return self._tab_id

    @property
    def label(self) -> str | None:
        return self._label

    @property
    def disabled(self) -> bool:
        return self._disabled


class _TabsImpl(BootstrapElement):
    """Private Tabs implementation. Tab children become a tablist plus panes."""

    component_name = "Tabs"
    children_kind = "grouping"
    reserved_classes: tuple[str, ...] = ()

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        active_tab: str | None = None,
        card: bool = False,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        persist, lazy, on_change = self._consume_surface_kwargs(kwargs)
        parsed = _coerce_tab_children(children)
        self._card = bool(card)
        self._lazy = lazy
        self._persist = persist
        self._on_change = on_change
        self._requested_active = active_tab
        self._active_tab = active_tab
        self._tabs: list[Any] = []
        self._buttons: dict[str, Element] = {}
        self._nav_items: dict[str, Element] = {}
        self._lazy_held: list[Any] = []
        self._header: Element | None = None
        self._body: Element | None = None
        self._structural_classes = tuple(tabs_structural_classes(card=self._card))
        super().__init__(None, tag="div", **kwargs)
        self._build_chrome()
        self._tabs.extend(parsed)
        assigned = assign_tab_ids([tab._explicit_tab_id for tab in self._tabs])
        for tab, tab_id in zip(self._tabs, assigned, strict=True):
            tab._tab_id = tab_id
        self._restore_persist()
        self._ensure_active()
        for tab in self._tabs:
            self._mount_pane(tab)
            self._create_nav_item(tab)
        self._apply_active_classes()
        self._persist_save()

    def _consume_surface_kwargs(
        self,
        kwargs: dict[str, Any],
    ) -> tuple[str, bool, Callable[..., Any] | None]:
        if self._surface == "compat":
            for native_only in ("lazy", "on_change", "persist"):
                if native_only in kwargs:
                    raise UnsupportedPropError(native_only)
            persistence = kwargs.pop("persistence", None)
            kwargs.pop("persisted_props", None)
            persistence_type = kwargs.pop("persistence_type", None)
            kwargs.pop("key", None)
            kwargs.pop("loading_state", None)
            persist = "off"
            if persistence:
                if persistence_type in {"local", "session", "memory"}:
                    persist = str(persistence_type)
                else:
                    persist = "local"
            return persist, False, None
        persist = kwargs.pop("persist", "off")
        if persist not in _PERSIST_VALUES:
            allowed = ", ".join(repr(item) for item in _PERSIST_VALUES)
            raise ValueError(f"persist must be one of {allowed}, got {persist!r}")
        lazy = bool(kwargs.pop("lazy", False))
        on_change = kwargs.pop("on_change", None)
        return str(persist), lazy, on_change

    def _build_chrome(self) -> None:
        with self:
            if self._card:
                self._header = ui.element("div")
                self._header.classes(" ".join(tabs_card_header_classes()))
                with self._header:
                    self._nav = ui.element("ul")
                    self._nav.classes(" ".join(tabs_nav_classes(card=True)))
                self._body = ui.element("div")
                self._body.classes(" ".join(tabs_card_body_classes()))
                with self._body:
                    self._content = ui.element("div")
                    self._content.classes(" ".join(tabs_content_classes()))
            else:
                self._nav = ui.element("ul")
                self._nav.classes(" ".join(tabs_nav_classes(card=False)))
                self._content = ui.element("div")
                self._content.classes(" ".join(tabs_content_classes()))
        self._nav._props["role"] = "tablist"
        self._nav.on("keydown", self._on_tablist_keydown, js_handler=_TABLIST_KEYDOWN)

    def _on_tablist_keydown(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def __exit__(self, *args: Any) -> Any:
        result = super().__exit__(*args)
        self._sync_tabs()
        return result

    @property
    def active_tab(self) -> str | None:
        self._sync_tabs()
        return self._active_tab

    @active_tab.setter
    def active_tab(self, value: str | None) -> None:
        self._sync_tabs()
        self._requested_active = value
        self._active_tab = value
        if value is None:
            self._ensure_active()
        self._apply_active_classes()
        self._persist_save()

    @property
    def tab_ids(self) -> list[str]:
        self._sync_tabs()
        return [tab.tab_id for tab in self._tabs if tab.tab_id is not None]

    def _persist_key(self) -> str | None:
        public = self._props.get("id")
        if isinstance(public, str) and public:
            return public
        return None

    def _restore_persist(self) -> None:
        if self._persist == "off" or self._requested_active is not None:
            return
        key = self._persist_key()
        if key is None:
            return
        remembered = _ACTIVE_TAB_MEMORY.get(key)
        known = {tab.tab_id for tab in self._tabs}
        if remembered and remembered in known:
            self._active_tab = remembered

    def _persist_save(self) -> None:
        if self._persist == "off" or self._active_tab is None:
            return
        key = self._persist_key()
        if key is not None:
            _ACTIVE_TAB_MEMORY[key] = self._active_tab

    def _ensure_active(self) -> None:
        ids = [tab.tab_id for tab in self._tabs if tab.tab_id is not None]
        disabled = [tab.disabled for tab in self._tabs]
        if self._active_tab is not None and self._active_tab in ids:
            return
        self._active_tab = first_enabled_tab_id(ids, disabled)

    def _find_tab(self, tab_id: str) -> Any | None:
        for tab in self._tabs:
            if tab.tab_id == tab_id:
                return tab
        return None

    def _mount_pane(self, tab: Any) -> None:
        selected = tab.tab_id == self._active_tab
        if self._lazy and not selected:
            if tab not in self._lazy_held:
                self._lazy_held.append(tab)
            return
        if tab in self._lazy_held:
            self._lazy_held.remove(tab)
        tab.move(self._content)
        _set_class(tab, "active", selected)

    def _create_nav_item(self, tab: Any) -> None:
        tab_id = tab.tab_id
        if tab_id is None or tab_id in self._buttons:
            return
        selected = tab_id == self._active_tab
        with self._nav:
            item = ui.element("li")
            item.classes(" ".join(tabs_nav_item_classes()))
            item._props["role"] = "presentation"
            with item:
                btn = ui.element("button")
                btn.classes(" ".join(tab_link_classes(active=selected, disabled=tab.disabled)))
                btn._props["type"] = "button"
                if tab._tab_class_name:
                    btn.classes(tab._tab_class_name)
                if tab._label_class_name:
                    btn.classes(tab._label_class_name)
                _apply_style(btn, tab._tab_style)
                _apply_style(btn, tab._label_style)
                if tab.disabled:
                    btn._props["disabled"] = True
                with btn:
                    ui.label(tab.label or "")
                btn.on("click", partial(self._on_tab_click, tab_id))
        self._nav_items[tab_id] = item
        self._buttons[tab_id] = btn

    def _on_tab_click(self, tab_id: str, *_args: Any, **_kwargs: Any) -> None:
        target = self._find_tab(tab_id)
        if target is None or target.disabled:
            return
        self._activate(tab_id, from_user=True)

    def _activate(self, tab_id: str, *, from_user: bool) -> None:
        if tab_id == self._active_tab:
            return
        self._active_tab = tab_id
        if self._lazy:
            tab = self._find_tab(tab_id)
            if tab is not None and tab in self._lazy_held:
                self._mount_pane(tab)
        self._apply_active_classes()
        self._persist_save()
        if from_user and self._on_change is not None:
            self._on_change(tab_id)

    def _apply_active_classes(self) -> None:
        for tab in self._tabs:
            tab_id = tab.tab_id
            if tab_id is None:
                continue
            selected = tab_id == self._active_tab
            pane_id = _pane_dom_id(tab)
            for key, value in tab_pane_aria(
                tab_id=tab_id,
                pane_id=pane_id,
                selected=selected,
            ).items():
                tab._props[key] = value
            _set_class(tab, "active", selected)
            tab.update()
            btn = self._buttons.get(tab_id)
            if btn is None:
                continue
            for key, value in tab_button_aria(
                tab_id=tab_id,
                pane_id=pane_id,
                selected=selected,
                disabled=tab.disabled,
            ).items():
                btn._props[key] = value
            _set_class(btn, "active", selected)
            _set_class(btn, "disabled", tab.disabled)
            if tab.disabled:
                btn._props["disabled"] = True
            elif "disabled" in btn._props:
                del btn._props["disabled"]
            btn.update()

    def _register_new_tab(self, tab: Any) -> None:
        if any(existing is tab for existing in self._tabs):
            return
        incoming = tab.tab_id if tab.tab_id else tab._explicit_tab_id
        assigned = assign_tab_ids([existing.tab_id for existing in self._tabs] + [incoming])
        tab._tab_id = assigned[-1]
        self._tabs.append(tab)
        if self._active_tab is None:
            self._ensure_active()
        self._mount_pane(tab)
        self._create_nav_item(tab)
        self._apply_active_classes()

    def _forget_tab(self, tab: Any) -> None:
        tab_id = tab.tab_id
        if tab_id is not None:
            item = self._nav_items.pop(tab_id, None)
            self._buttons.pop(tab_id, None)
            if item is not None:
                item.delete()
        if tab in self._lazy_held:
            self._lazy_held.remove(tab)
        if tab in self._tabs:
            self._tabs.remove(tab)

    def _sync_tabs(self) -> None:
        if getattr(self, "_content", None) is None:
            return
        loose = [child for child in _element_children(self) if _is_tab_element(child)]
        for tab in loose:
            self._register_new_tab(tab)
        present = [child for child in _element_children(self._content) if _is_tab_element(child)]
        present.extend(self._lazy_held)
        present_ids = {id(tab) for tab in present}
        for tab in list(self._tabs):
            if id(tab) not in present_ids:
                self._forget_tab(tab)
        known_ids = {tab.tab_id for tab in self._tabs}
        if self._active_tab not in known_ids:
            self._ensure_active()
            self._apply_active_classes()
            self._persist_save()


Tab, DbcTab = make_surface_classes("Tab", globals())
tab = Tab
Tabs, DbcTabs = make_surface_classes("Tabs", globals())
tabs = Tabs
