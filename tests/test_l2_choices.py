"""L2 tests for the choice family."""

from __future__ import annotations

from typing import Any

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components._base import ChildrenError, PropConflictError
from nicegui_bootstrap_components.bs._choices import (
    Checkbox,
    Checklist,
    DbcCheckbox,
    DbcChecklist,
    DbcRadioButton,
    DbcRadioItems,
    DbcSelect,
    DbcSwitch,
    RadioButton,
    RadioItems,
    Select,
    Switch,
    checkbox,
    checklist,
    choice_input_classes,
    choice_label_classes,
    form_check_item_classes,
    normalize_choice_options,
    radio_button,
    radio_items,
    select,
    select_structural_classes,
    switch,
)

pytest_plugins = ["nicegui.testing.plugin"]


def _child_elements(element: Any) -> list[Any]:
    slot = getattr(element, "default_slot", None)
    if slot is not None:
        return list(slot.children)
    slots = getattr(element, "slots", None)
    if isinstance(slots, dict) and "default" in slots:
        return list(slots["default"].children)
    try:
        return list(element)
    except TypeError:
        return []


def _by_tag(element: Any, tag: str) -> list[Any]:
    found: list[Any] = []
    for child in _child_elements(element):
        if getattr(child, "tag", None) == tag:
            found.append(child)
        found.extend(_by_tag(child, tag))
    return found


def _has_class(element: Any, name: str) -> bool:
    classes = getattr(element, "_classes", [])
    if name in classes:
        return True
    joined = " ".join(str(item) for item in classes)
    return name in joined.split()


def test_normalize_choice_options_list_of_scalars() -> None:
    assert normalize_choice_options(["a", "b"]) == [
        {
            "value": "a",
            "label": "a",
            "disabled": False,
            "title": None,
            "input_id": None,
            "label_id": None,
        },
        {
            "value": "b",
            "label": "b",
            "disabled": False,
            "title": None,
            "input_id": None,
            "label_id": None,
        },
    ]
    assert normalize_choice_options([1, 2]) == [
        {
            "value": 1,
            "label": "1",
            "disabled": False,
            "title": None,
            "input_id": None,
            "label_id": None,
        },
        {
            "value": 2,
            "label": "2",
            "disabled": False,
            "title": None,
            "input_id": None,
            "label_id": None,
        },
    ]
    assert normalize_choice_options(("a",))[0]["value"] == "a"


def test_normalize_choice_options_dicts() -> None:
    assert normalize_choice_options(
        [
            {
                "label": "Alpha",
                "value": "a",
                "disabled": True,
                "title": "tip",
                "input_id": "i1",
                "label_id": "l1",
            }
        ]
    ) == [
        {
            "value": "a",
            "label": "Alpha",
            "disabled": True,
            "title": "tip",
            "input_id": "i1",
            "label_id": "l1",
        }
    ]
    assert normalize_choice_options([{"value": "only"}])[0]["label"] == "only"
    assert normalize_choice_options([{"label": "Only"}])[0]["value"] == "Only"


def test_normalize_choice_options_dict_preserves_insertion_order() -> None:
    options = {"z": "Zed", "a": "Aye", "m": "Em"}
    normalized = normalize_choice_options(options)
    assert [item["value"] for item in normalized] == ["z", "a", "m"]
    assert [item["label"] for item in normalized] == ["Zed", "Aye", "Em"]
    numeric = {3: "three", 1: "one", 2: "two"}
    assert [item["value"] for item in normalize_choice_options(numeric)] == [3, 1, 2]


def test_normalize_choice_options_empty_and_invalid() -> None:
    assert normalize_choice_options(None) == []
    assert normalize_choice_options([]) == []
    assert normalize_choice_options({}) == []
    with pytest.raises(ValueError, match="options"):
        normalize_choice_options(123)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="options"):
        normalize_choice_options("ab")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Option"):
        normalize_choice_options([{"disabled": True}])
    with pytest.raises(ValueError, match="Invalid option"):
        normalize_choice_options([["nested"]])


def test_select_structural_classes() -> None:
    assert select_structural_classes() == ["form-select"]
    assert select_structural_classes(size="md") == ["form-select"]
    assert select_structural_classes(size="sm") == ["form-select", "form-select-sm"]
    assert select_structural_classes(size="lg") == ["form-select", "form-select-lg"]
    assert select_structural_classes(valid=True) == ["form-select", "is-valid"]
    assert select_structural_classes(invalid=True) == ["form-select", "is-invalid"]
    assert select_structural_classes(size="sm", valid=True) == [
        "form-select",
        "form-select-sm",
        "is-valid",
    ]
    with pytest.raises(ValueError, match="size"):
        select_structural_classes(size="xl")
    with pytest.raises(PropConflictError):
        select_structural_classes(valid=True, invalid=True)


def test_form_check_item_classes() -> None:
    assert form_check_item_classes() == ["form-check"]
    assert form_check_item_classes(inline=True) == ["form-check", "form-check-inline"]
    assert form_check_item_classes(switch=True) == ["form-check", "form-switch"]
    assert form_check_item_classes(inline=True, switch=True) == [
        "form-check",
        "form-check-inline",
        "form-switch",
    ]


def test_choice_input_and_label_classes() -> None:
    assert choice_input_classes() == ["form-check-input"]
    assert choice_input_classes(input_class_name="x") == ["form-check-input", "x"]
    assert choice_input_classes(input_checked_class_name="c", checked=True) == [
        "form-check-input",
        "c",
    ]
    assert choice_input_classes(input_checked_class_name="c", checked=False) == ["form-check-input"]
    assert choice_input_classes(
        input_class_name="foo bar",
        input_checked_class_name="on",
        checked=True,
    ) == ["form-check-input", "foo", "bar", "on"]
    assert choice_label_classes() == ["form-check-label"]
    assert choice_label_classes(label_class_name="cap", checked=False) == [
        "form-check-label",
        "cap",
    ]
    assert choice_label_classes(
        label_class_name="cap",
        label_checked_class_name="picked",
        checked=True,
    ) == ["form-check-label", "cap", "picked"]


def test_surface_identities() -> None:
    assert Select is not DbcSelect
    assert select is Select
    assert Select.component_name == "Select"
    assert DbcSelect.component_name == "Select"

    assert Checkbox is not DbcCheckbox
    assert checkbox is Checkbox
    assert Checkbox.component_name == "Checkbox"
    assert DbcCheckbox.component_name == "Checkbox"

    assert RadioButton is not DbcRadioButton
    assert radio_button is RadioButton
    assert RadioButton.component_name == "RadioButton"
    assert DbcRadioButton.component_name == "RadioButton"

    assert Switch is not DbcSwitch
    assert switch is Switch
    assert Switch.component_name == "Switch"
    assert DbcSwitch.component_name == "Switch"

    assert Checklist is not DbcChecklist
    assert checklist is Checklist
    assert Checklist.component_name == "Checklist"
    assert DbcChecklist.component_name == "Checklist"

    assert RadioItems is not DbcRadioItems
    assert radio_items is RadioItems
    assert RadioItems.component_name == "RadioItems"
    assert DbcRadioItems.component_name == "RadioItems"


def test_select_validation_before_construction() -> None:
    with pytest.raises(ValueError, match="size"):
        Select(size="xl")
    with pytest.raises(ValueError, match="size"):
        DbcSelect(size="huge")
    with pytest.raises(PropConflictError):
        Select(valid=True, invalid=True)
    with pytest.raises(PropConflictError):
        DbcSelect(valid=True, invalid=True)


def test_form_check_and_group_reject_children() -> None:
    with pytest.raises(ChildrenError):
        Checkbox("text")
    with pytest.raises(ChildrenError):
        Switch("text")
    with pytest.raises(ChildrenError):
        RadioButton("text")
    with pytest.raises(ChildrenError):
        Checklist("text")
    with pytest.raises(ChildrenError):
        RadioItems("text")
    with pytest.raises(ChildrenError):
        DbcCheckbox(children=["nope"])
    with pytest.raises(ChildrenError):
        DbcChecklist(children=["nope"])


@pytest.mark.user
async def test_select_renders(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        sel = Select(
            options=["one", "two"],
            value="one",
            placeholder="Pick",
            size="sm",
            html_size=3,
            name="city",
        )
        assert sel.tag == "select"
        assert _has_class(sel, "form-select")
        assert _has_class(sel, "form-select-sm")
        assert sel._props.get("size") == 3
        assert sel._props.get("name") == "city"
        assert sel.value == "one"
        assert sel._props.get("model-value") == "one"
        kids = _child_elements(sel)
        assert len(kids) == 3
        assert kids[0].tag == "option"
        assert kids[0]._props.get("value") == ""
        assert kids[0]._props.get("disabled") is True
        assert kids[0]._props.get("hidden") is True
        assert getattr(kids[0], "_text", None) == "Pick"
        assert kids[1]._props.get("value") == "one"
        assert kids[1]._props.get("selected") is True
        assert getattr(kids[1], "_text", None) == "one"
        assert kids[2]._props.get("value") == "two"
        assert "selected" not in kids[2]._props

        sized = Select(options={"x": "X-ray", "y": "Yankee"}, size="md", valid=True)
        assert _has_class(sized, "form-select")
        assert not _has_class(sized, "form-select-md")
        assert _has_class(sized, "is-valid")
        opt_values = [child._props.get("value") for child in _child_elements(sized)]
        assert opt_values == ["x", "y"]

    await user.open("/")
    await user.should_see("one")


@pytest.mark.user
async def test_form_check_controls_render(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        cb = Checkbox(label="Agree", value=True, name="tos")
        assert cb.tag == "div"
        assert _has_class(cb, "form-check")
        assert not _has_class(cb, "form-switch")
        inputs = _by_tag(cb, "input")
        labels = _by_tag(cb, "label")
        assert len(inputs) == 1
        assert inputs[0]._props.get("type") == "checkbox"
        assert inputs[0]._props.get("checked") is True
        assert inputs[0]._props.get("name") == "tos"
        assert labels[0]._props.get("for") == inputs[0]._props.get("id")
        assert getattr(labels[0], "_text", None) == "Agree"
        assert cb.value is True
        assert cb._props.get("model-value") is True

        sw = Switch(label="Notify", value=False)
        assert _has_class(sw, "form-check")
        assert _has_class(sw, "form-switch")
        sw_inputs = _by_tag(sw, "input")
        assert sw_inputs[0]._props.get("type") == "checkbox"
        assert "checked" not in sw_inputs[0]._props
        assert sw._props.get("model-value") is False

        rb = RadioButton(label="Choice A", value=True, name="g1")
        rb_inputs = _by_tag(rb, "input")
        assert rb_inputs[0]._props.get("type") == "radio"
        assert rb_inputs[0]._props.get("name") == "g1"
        assert rb_inputs[0]._props.get("checked") is True
        assert rb.value is True
        assert rb._props.get("model-value") is True

    await user.open("/")
    await user.should_see("Agree")


@pytest.mark.user
async def test_choice_groups_render(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        cl = Checklist(
            options=["x", "y", "dropped"],
            value=["x", "missing"],
            inline=True,
            switch=True,
            name="c",
        )
        assert cl.tag == "div"
        assert cl.value == ["x"]
        assert cl._props.get("model-value") == ["x"]
        wrappers = _child_elements(cl)
        assert len(wrappers) == 3
        assert _has_class(wrappers[0], "form-check")
        assert _has_class(wrappers[0], "form-check-inline")
        assert _has_class(wrappers[0], "form-switch")
        inp0 = _by_tag(wrappers[0], "input")[0]
        inp1 = _by_tag(wrappers[1], "input")[0]
        assert inp0._props.get("type") == "checkbox"
        assert inp0._props.get("checked") is True
        assert inp0._props.get("value") == "x"
        assert inp0._props.get("name") == "c"
        assert "checked" not in inp1._props
        assert getattr(_by_tag(wrappers[0], "label")[0], "_text", None) == "x"

        ri = RadioItems(
            options=[
                {"label": "P", "value": "p"},
                {"label": "Q", "value": "q", "disabled": True},
            ],
            value="p",
        )
        assert ri.value == "p"
        assert ri._props.get("model-value") == "p"
        ri_inputs = _by_tag(ri, "input")
        assert len(ri_inputs) == 2
        assert ri_inputs[0]._props.get("type") == "radio"
        assert ri_inputs[1]._props.get("type") == "radio"
        assert ri_inputs[0]._props.get("checked") is True
        assert ri_inputs[1]._props.get("disabled") is True
        assert ri_inputs[0]._props.get("name") == ri_inputs[1]._props.get("name")
        assert ri_inputs[0]._props.get("name")
        assert getattr(_by_tag(ri, "label")[0], "_text", None) == "P"

        numeric = RadioItems(options=[{"label": "One", "value": 1}, 2], value=1)
        assert numeric.value == 1
        assert _by_tag(numeric, "input")[0]._props.get("value") == "1"

    await user.open("/")
    await user.should_see("P")
