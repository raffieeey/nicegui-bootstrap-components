"""Choice family: Select, Checkbox, Switch, RadioButton, Checklist, RadioItems."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nicegui.element import Element

from .._base import (
    BootstrapValueElement,
    ChildrenError,
    PropConflictError,
    make_surface_classes,
    normalize_style,
    style_to_css,
)
from .._host import set_element_text

__all__ = [
    "Select",
    "DbcSelect",
    "select",
    "Checkbox",
    "DbcCheckbox",
    "checkbox",
    "RadioButton",
    "DbcRadioButton",
    "radio_button",
    "Switch",
    "DbcSwitch",
    "switch",
    "Checklist",
    "DbcChecklist",
    "checklist",
    "RadioItems",
    "DbcRadioItems",
    "radio_items",
    "normalize_choice_options",
    "select_structural_classes",
    "form_check_item_classes",
    "choice_input_classes",
    "choice_label_classes",
]

_SELECT_SIZES = {"sm", "md", "lg"}

_JS_SELECT_CHANGE = """(e) => {
  const root = e.currentTarget || e.target;
  let sel = e.target;
  if (!sel || sel.tagName !== 'SELECT') {
    sel = root && root.tagName === 'SELECT' ? root : sel;
  }
  if (!sel || sel.tagName !== 'SELECT') return;
  emit(sel.value == null ? '' : String(sel.value));
}"""

_JS_CHECK_CHANGE = """(e) => {
  const root = e.currentTarget || e.target;
  let input = e.target;
  if (!input || input.tagName !== 'INPUT') {
    input = root && root.querySelector ? root.querySelector('input') : input;
  }
  if (!input) return;
  emit(!!input.checked);
}"""

_JS_CHECKLIST_CHANGE = """(e) => {
  const root = e.currentTarget || e.target;
  if (!root || !root.querySelectorAll) return;
  const checked = [];
  root.querySelectorAll('input[type="checkbox"]').forEach((el) => {
    if (el.checked) checked.push(el.value == null ? '' : String(el.value));
  });
  emit(checked);
}"""

_JS_RADIO_ITEMS_CHANGE = """(e) => {
  const root = e.currentTarget || e.target;
  if (!root || !root.querySelector) return;
  const selected = root.querySelector('input[type="radio"]:checked');
  emit(selected && selected.value != null ? String(selected.value) : null);
}"""


def _split_classes(value: str | None) -> list[str]:
    if not value:
        return []
    return [part for part in value.split() if part]


def _resolve_alias(primary: Any, fallback: Any) -> Any:
    if primary is not None:
        return primary
    return fallback


def _html_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _payload_from_event(e: Any) -> Any:
    return getattr(e, "args", e)


def _set_flag(element: Any, name: str, value: bool) -> None:
    props = element._props
    if value:
        props[name] = True
    else:
        props.pop(name, None)


def _apply_style_dict(element: Element, style: dict[str, Any] | str | None) -> None:
    if not style:
        return
    if isinstance(style, str):
        element.style(style)
        return
    normalized = normalize_style(style)
    if isinstance(normalized, str):
        if normalized:
            element.style(normalized)
        return
    css = style_to_css(normalized)
    if css:
        element.style(css)


def _has_children(children: object) -> bool:
    if children is None:
        return False
    return not (children == [] or children == ())


def _normalize_one_option(item: Any) -> dict[str, Any]:
    if isinstance(item, dict):
        if "value" not in item and "label" not in item:
            raise ValueError("Option dict requires 'label' or 'value'")
        value = item["value"] if "value" in item else item["label"]
        raw_label = item.get("label", value)
        title = item.get("title")
        return {
            "value": value,
            "label": "" if raw_label is None else str(raw_label),
            "disabled": bool(item.get("disabled", False)),
            "title": None if title is None else str(title),
            "input_id": item.get("input_id"),
            "label_id": item.get("label_id"),
        }
    if isinstance(item, (list, tuple)):
        raise ValueError(f"Invalid option {item!r}; expected a string, number, or dict")
    return {
        "value": item,
        "label": "" if item is None else str(item),
        "disabled": False,
        "title": None,
        "input_id": None,
        "label_id": None,
    }


def normalize_choice_options(
    options: list[Any] | dict[Any, Any] | tuple[Any, ...] | None,
) -> list[dict[str, Any]]:
    """Normalize choice options to dicts with label, value, disabled, title, and ids."""
    if options is None:
        return []
    if isinstance(options, dict):
        items = [{"value": key, "label": val} for key, val in options.items()]
        return [_normalize_one_option(item) for item in items]
    if isinstance(options, (list, tuple)):
        return [_normalize_one_option(item) for item in options]
    raise ValueError(f"options must be a list, tuple, or dict, not {type(options).__name__}")


def select_structural_classes(
    *,
    size: str | None = None,
    valid: bool | None = None,
    invalid: bool | None = None,
) -> list[str]:
    """Return Bootstrap ``form-select`` classes. Unknown sizes raise ``ValueError``."""
    if size is not None and size not in _SELECT_SIZES:
        raise ValueError(f"Invalid Select size {size!r}; expected one of 'sm', 'md', 'lg'")
    if valid and invalid:
        raise PropConflictError("valid", "invalid")
    classes = ["form-select"]
    if size in {"sm", "lg"}:
        classes.append(f"form-select-{size}")
    if valid:
        classes.append("is-valid")
    if invalid:
        classes.append("is-invalid")
    return classes


def form_check_item_classes(*, inline: bool = False, switch: bool = False) -> list[str]:
    """Return Bootstrap ``form-check`` wrapper classes for a choice item."""
    classes = ["form-check"]
    if inline:
        classes.append("form-check-inline")
    if switch:
        classes.append("form-switch")
    return classes


def choice_input_classes(
    *,
    input_class_name: str | None = None,
    input_checked_class_name: str | None = None,
    checked: bool = False,
) -> list[str]:
    """Return classes for a ``form-check-input`` element."""
    classes = ["form-check-input"]
    classes.extend(_split_classes(input_class_name))
    if checked:
        classes.extend(_split_classes(input_checked_class_name))
    return classes


def choice_label_classes(
    *,
    label_class_name: str | None = None,
    label_checked_class_name: str | None = None,
    checked: bool = False,
) -> list[str]:
    """Return classes for a ``form-check-label`` element."""
    classes = ["form-check-label"]
    classes.extend(_split_classes(label_class_name))
    if checked:
        classes.extend(_split_classes(label_checked_class_name))
    return classes


def _option_is_selected(option_value: Any, current: Any, *, multi: bool) -> bool:
    if multi:
        if current is None:
            return False
        for item in current:
            if item == option_value or _html_value(item) == _html_value(option_value):
                return True
        return False
    if current is None:
        return False
    return current == option_value or _html_value(current) == _html_value(option_value)


def _match_option_value(value: Any, normalized: list[dict[str, Any]]) -> Any | None:
    for opt in normalized:
        if opt["value"] == value or _html_value(opt["value"]) == _html_value(value):
            return opt["value"]
    return None


def _filter_selected(values: list[Any], normalized: list[dict[str, Any]]) -> list[Any]:
    filtered: list[Any] = []
    seen: set[int] = set()
    for item in values:
        for index, opt in enumerate(normalized):
            if opt["value"] == item or _html_value(opt["value"]) == _html_value(item):
                if index not in seen:
                    filtered.append(opt["value"])
                    seen.add(index)
                break
    return filtered


def _make_option_element(
    *,
    value: str,
    label: str,
    disabled: bool = False,
    title: str | None = None,
    selected: bool = False,
    hidden: bool = False,
) -> Element:
    element = Element("option")
    element._props["value"] = value
    set_element_text(element, label)
    if disabled:
        element._props["disabled"] = True
    if selected:
        element._props["selected"] = True
    if hidden:
        element._props["hidden"] = True
    if title:
        element._props["title"] = title
    return element


def _mount_form_check(
    parent: BootstrapValueElement,
    *,
    input_type: str,
    checked: bool,
    disabled: bool,
    label: str | None,
    name: str | None,
    input_id: str | None,
    label_id: str | None,
    input_class_name: str | None,
    input_style: dict[str, Any] | str | None,
    label_class_name: str | None,
    label_style: dict[str, Any] | str | None,
) -> tuple[Element, Element]:
    with parent:
        input_el = Element("input")
        input_el._classes.extend(
            choice_input_classes(input_class_name=input_class_name, checked=checked)
        )
        input_el._props["type"] = input_type
        if checked:
            input_el._props["checked"] = True
        if disabled:
            input_el._props["disabled"] = True
        if name is not None:
            input_el._props["name"] = name
        if input_id is not None:
            input_el._props["id"] = input_id
        _apply_style_dict(input_el, input_style)
        label_el = Element("label")
        label_el._classes.extend(
            choice_label_classes(label_class_name=label_class_name, checked=checked)
        )
        set_element_text(label_el, "" if label is None else label)
        if label_id is not None:
            label_el._props["id"] = label_id
        if input_id is not None:
            label_el._props["for"] = input_id
        _apply_style_dict(label_el, label_style)
    return input_el, label_el


def _merged_style(
    base: dict[str, Any] | str | None,
    extra: dict[str, Any] | str | None,
    *,
    use_extra: bool,
) -> dict[str, Any] | str | None:
    if not use_extra or extra is None:
        return base
    if base is None:
        return extra
    if isinstance(base, dict) and isinstance(extra, dict):
        merged = dict(base)
        merged.update(extra)
        return merged
    return extra


def _mount_choice_item(
    parent: BootstrapValueElement,
    *,
    input_type: str,
    option: dict[str, Any],
    checked: bool,
    inline: bool,
    switch: bool,
    name: str | None,
    input_class_name: str | None,
    input_checked_class_name: str | None,
    input_style: dict[str, Any] | str | None,
    input_checked_style: dict[str, Any] | str | None,
    label_class_name: str | None,
    label_checked_class_name: str | None,
    label_style: dict[str, Any] | str | None,
    label_checked_style: dict[str, Any] | str | None,
    input_id: str | None,
) -> tuple[Element, Element, Element]:
    with parent:
        wrapper = Element("div")
        wrapper._classes.extend(form_check_item_classes(inline=inline, switch=switch))
        with wrapper:
            input_el = Element("input")
            input_el._classes.extend(
                choice_input_classes(
                    input_class_name=input_class_name,
                    input_checked_class_name=input_checked_class_name,
                    checked=checked,
                )
            )
            input_el._props["type"] = input_type
            input_el._props["value"] = _html_value(option["value"])
            if checked:
                input_el._props["checked"] = True
            if option["disabled"]:
                input_el._props["disabled"] = True
            if name is not None:
                input_el._props["name"] = name
            if input_id is not None:
                input_el._props["id"] = input_id
            _apply_style_dict(
                input_el,
                _merged_style(input_style, input_checked_style, use_extra=checked),
            )
            label_el = Element("label")
            label_el._classes.extend(
                choice_label_classes(
                    label_class_name=label_class_name,
                    label_checked_class_name=label_checked_class_name,
                    checked=checked,
                )
            )
            set_element_text(label_el, option["label"])
            label_id = option.get("label_id")
            if label_id is not None:
                label_el._props["id"] = label_id
            if input_id is not None:
                label_el._props["for"] = input_id
            _apply_style_dict(
                label_el,
                _merged_style(label_style, label_checked_style, use_extra=checked),
            )
    return wrapper, input_el, label_el


class _SelectImpl(BootstrapValueElement):
    """Private Select implementation."""

    component_name = "Select"
    children_kind = "grouping"
    reserved_classes = ("form-select",)

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        value: Any = None,
        options: list[Any] | dict[Any, Any] | tuple[Any, ...] | None = None,
        placeholder: str | None = None,
        size: str | None = None,
        html_size: int | None = None,
        disabled: bool = False,
        required: bool = False,
        valid: bool | None = None,
        invalid: bool | None = None,
        name: str | None = None,
        on_change: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        self._normalized_options = normalize_choice_options(options)
        self._structural_classes = tuple(
            select_structural_classes(size=size, valid=valid, invalid=invalid)
        )
        use_options = options is not None
        super().__init__(
            None if use_options else children,
            value=value,
            on_change=on_change,
            tag="select",
            **kwargs,
        )
        if html_size is not None:
            self._props["size"] = int(html_size)
        _set_flag(self, "disabled", disabled)
        _set_flag(self, "required", required)
        if name is not None:
            self._props["name"] = name
        if use_options:
            current = self.value
            current_html = None if current is None or current == "" else _html_value(current)
            matched = False
            if current_html is not None:
                matched = any(
                    _html_value(opt["value"]) == current_html for opt in self._normalized_options
                )
            with self:
                if placeholder is not None:
                    _make_option_element(
                        value="",
                        label=placeholder,
                        disabled=True,
                        hidden=True,
                        selected=not matched,
                    )
                for opt in self._normalized_options:
                    selected = (
                        current_html is not None and _html_value(opt["value"]) == current_html
                    )
                    _make_option_element(
                        value=_html_value(opt["value"]),
                        label=opt["label"],
                        disabled=bool(opt["disabled"]),
                        title=opt["title"],
                        selected=selected,
                    )
        self.on("change", self._on_dom_change, js_handler=_JS_SELECT_CHANGE)

    def _on_dom_change(self, e: Any) -> None:
        payload = _payload_from_event(e)
        if isinstance(payload, list):
            payload = payload[0] if payload else ""
        if payload is None or payload == "":
            self.value = None
            return
        self.value = str(payload)


Select, DbcSelect = make_surface_classes("Select", globals())
select = Select


class _FormCheckControlImpl(BootstrapValueElement):
    """Shared boolean form-check control (checkbox, switch, radio)."""

    component_name = "Checkbox"
    children_kind = "grouping"
    reserved_classes: tuple[str, ...] = ("form-check",)
    _input_type: str = "checkbox"
    _switch: bool = False

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        value: bool = False,
        disabled: bool = False,
        label: str | None = None,
        name: str | None = None,
        input_id: str | None = None,
        label_id: str | None = None,
        input_class_name: str | None = None,
        inputClassName: str | None = None,
        input_style: dict[str, Any] | str | None = None,
        label_class_name: str | None = None,
        labelClassName: str | None = None,
        label_style: dict[str, Any] | str | None = None,
        on_change: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        if _has_children(children):
            raise ChildrenError(
                f"{self.component_name} does not accept children; use the label property instead"
            )
        self._structural_classes = tuple(form_check_item_classes(switch=self._switch))
        super().__init__(
            None,
            value=bool(value),
            on_change=on_change,
            tag="div",
            **kwargs,
        )
        resolved_input_id = input_id or f"nbc-{self.component_name.lower()}-{self.id}"
        self._input, self._label = _mount_form_check(
            self,
            input_type=self._input_type,
            checked=bool(self.value),
            disabled=disabled,
            label=label,
            name=name,
            input_id=resolved_input_id,
            label_id=label_id,
            input_class_name=_resolve_alias(input_class_name, inputClassName),
            input_style=input_style,
            label_class_name=_resolve_alias(label_class_name, labelClassName),
            label_style=label_style,
        )
        self.on("change", self._on_dom_change, js_handler=_JS_CHECK_CHANGE)

    def _handle_value_change(self, *args: Any, **kwargs: Any) -> None:
        inherited = getattr(super(), "_handle_value_change", None)
        if callable(inherited):
            inherited(*args, **kwargs)
        self._sync_to_dom()

    def _sync_to_dom(self) -> None:
        input_el = getattr(self, "_input", None)
        if input_el is None:
            return
        _set_flag(input_el, "checked", bool(self.value))
        updater = getattr(input_el, "update", None)
        if callable(updater):
            updater()

    def _on_dom_change(self, e: Any) -> None:
        payload = _payload_from_event(e)
        if isinstance(payload, list):
            payload = payload[0] if payload else False
        self.value = bool(payload)


class _CheckboxImpl(_FormCheckControlImpl):
    """Private Checkbox implementation."""

    component_name = "Checkbox"


class _SwitchImpl(_FormCheckControlImpl):
    """Private Switch implementation."""

    component_name = "Switch"
    reserved_classes = ("form-check", "form-switch")
    _switch = True


class _RadioButtonImpl(_FormCheckControlImpl):
    """Private RadioButton implementation."""

    component_name = "RadioButton"
    _input_type = "radio"


Checkbox, DbcCheckbox = make_surface_classes("Checkbox", globals())
checkbox = Checkbox

Switch, DbcSwitch = make_surface_classes("Switch", globals())
switch = Switch

RadioButton, DbcRadioButton = make_surface_classes("RadioButton", globals())
radio_button = RadioButton


class _ChoiceGroupImpl(BootstrapValueElement):
    """Shared options group for Checklist and RadioItems."""

    component_name = "Checklist"
    children_kind = "grouping"
    reserved_classes: tuple[str, ...] = ()
    _input_type: str = "checkbox"
    _multi: bool = True

    def __init__(
        self,
        children: object = None,
        *,
        _surface: str,
        value: Any = None,
        options: list[Any] | dict[Any, Any] | tuple[Any, ...] | None = None,
        inline: bool = False,
        switch: bool = False,
        disabled: bool = False,
        name: str | None = None,
        input_class_name: str | None = None,
        inputClassName: str | None = None,
        input_style: dict[str, Any] | str | None = None,
        input_checked_class_name: str | None = None,
        inputCheckedClassName: str | None = None,
        input_checked_style: dict[str, Any] | str | None = None,
        inputCheckedStyle: dict[str, Any] | str | None = None,
        label_class_name: str | None = None,
        labelClassName: str | None = None,
        label_style: dict[str, Any] | str | None = None,
        label_checked_class_name: str | None = None,
        labelCheckedClassName: str | None = None,
        label_checked_style: dict[str, Any] | str | None = None,
        labelCheckedStyle: dict[str, Any] | str | None = None,
        on_change: Callable[..., Any] | None = None,
        **kwargs: Any,
    ) -> None:
        self._surface = _surface
        if _has_children(children):
            raise ChildrenError(
                f"{self.component_name} does not accept children; use the options property instead"
            )
        self._normalized_options = normalize_choice_options(options)
        if self._multi:
            incoming = list(value) if value is not None else []
            value = _filter_selected(incoming, self._normalized_options)
        elif value is not None:
            value = _match_option_value(value, self._normalized_options)
        self._structural_classes = ()
        self._inline = inline
        self._switch = switch
        self._name = name
        self._input_class_name = _resolve_alias(input_class_name, inputClassName)
        self._input_style = input_style
        self._input_checked_class_name = _resolve_alias(
            input_checked_class_name, inputCheckedClassName
        )
        self._input_checked_style = _resolve_alias(input_checked_style, inputCheckedStyle)
        self._label_class_name = _resolve_alias(label_class_name, labelClassName)
        self._label_style = label_style
        self._label_checked_class_name = _resolve_alias(
            label_checked_class_name, labelCheckedClassName
        )
        self._label_checked_style = _resolve_alias(label_checked_style, labelCheckedStyle)
        self._html_to_value = {
            _html_value(opt["value"]): opt["value"] for opt in self._normalized_options
        }
        super().__init__(None, value=value, on_change=on_change, tag="div", **kwargs)
        group_name = self._name
        if group_name is None and not self._multi:
            group_name = f"nbc-radioitems-{self.id}"
        self._item_refs: list[tuple[Element, Element, dict[str, Any]]] = []
        for index, opt in enumerate(self._normalized_options):
            checked = _option_is_selected(opt["value"], self.value, multi=self._multi)
            option_disabled = bool(opt["disabled"]) or disabled
            option = dict(opt)
            option["disabled"] = option_disabled
            input_id = opt["input_id"] or f"nbc-{self.component_name.lower()}-{self.id}-{index}"
            _wrapper, input_el, label_el = _mount_choice_item(
                self,
                input_type=self._input_type,
                option=option,
                checked=checked,
                inline=self._inline,
                switch=self._switch,
                name=group_name,
                input_class_name=self._input_class_name,
                input_checked_class_name=self._input_checked_class_name,
                input_style=self._input_style,
                input_checked_style=self._input_checked_style,
                label_class_name=self._label_class_name,
                label_checked_class_name=self._label_checked_class_name,
                label_style=self._label_style,
                label_checked_style=self._label_checked_style,
                input_id=input_id,
            )
            self._item_refs.append((input_el, label_el, opt))
        js_handler = _JS_CHECKLIST_CHANGE if self._multi else _JS_RADIO_ITEMS_CHANGE
        self.on("change", self._on_dom_change, js_handler=js_handler)

    def _restore_value(self, raw: Any) -> Any:
        text = _html_value(raw)
        if text in self._html_to_value:
            return self._html_to_value[text]
        return raw

    def _handle_value_change(self, *args: Any, **kwargs: Any) -> None:
        inherited = getattr(super(), "_handle_value_change", None)
        if callable(inherited):
            inherited(*args, **kwargs)
        self._sync_to_dom()

    def _sync_to_dom(self) -> None:
        items = getattr(self, "_item_refs", None)
        if not items:
            return
        current = self.value
        for input_el, _label_el, opt in items:
            checked = _option_is_selected(opt["value"], current, multi=self._multi)
            _set_flag(input_el, "checked", checked)
            updater = getattr(input_el, "update", None)
            if callable(updater):
                updater()

    def _on_dom_change(self, e: Any) -> None:
        payload = _payload_from_event(e)
        if self._multi:
            if payload is None:
                payload = []
            if not isinstance(payload, list):
                payload = [payload]
            self.value = [self._restore_value(item) for item in payload]
            return
        if isinstance(payload, list):
            payload = payload[0] if payload else None
        if payload is None or payload == "":
            self.value = None
            return
        self.value = self._restore_value(payload)


class _ChecklistImpl(_ChoiceGroupImpl):
    """Private Checklist implementation."""

    component_name = "Checklist"


class _RadioItemsImpl(_ChoiceGroupImpl):
    """Private RadioItems implementation."""

    component_name = "RadioItems"
    _input_type = "radio"
    _multi = False


Checklist, DbcChecklist = make_surface_classes("Checklist", globals())
checklist = Checklist

RadioItems, DbcRadioItems = make_surface_classes("RadioItems", globals())
radio_items = RadioItems
