"""L1 tests for the forms family."""

from __future__ import annotations

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components._base import UnsupportedPropError
from nicegui_bootstrap_components.bs._actions import Button
from nicegui_bootstrap_components.bs._forms import (
    DbcForm,
    DbcFormFeedback,
    DbcFormFloating,
    DbcFormText,
    DbcInputGroup,
    DbcInputGroupText,
    DbcLabel,
    Form,
    FormFeedback,
    FormFloating,
    FormText,
    InputGroup,
    InputGroupText,
    Label,
    form,
    form_feedback,
    form_feedback_classes,
    form_floating,
    form_method,
    form_text,
    form_text_classes,
    input_group,
    input_group_classes,
    input_group_text,
    label,
    label_classes,
)

pytest_plugins = ["nicegui.testing.plugin"]
pytestmark = pytest.mark.user


def test_label_classes_default() -> None:
    assert label_classes() == ["form-label"]


def test_label_classes_hidden() -> None:
    assert label_classes(hidden=True) == ["form-label", "visually-hidden"]


def test_label_classes_size_sm() -> None:
    assert label_classes(size="sm") == ["form-label", "col-form-label", "col-form-label-sm"]


def test_label_classes_size_lg() -> None:
    assert label_classes(size="lg") == ["form-label", "col-form-label", "col-form-label-lg"]


def test_label_classes_size_md() -> None:
    assert label_classes(size="md") == ["form-label"]


def test_label_classes_size_xl_raises() -> None:
    with pytest.raises(ValueError):
        label_classes(size="xl")


def test_label_classes_check() -> None:
    assert "form-check-label" in label_classes(check=True)


def test_label_classes_color() -> None:
    assert "text-primary" in label_classes(color="primary")


def test_form_method_get_and_post_ok() -> None:
    assert form_method("GET") == "GET"
    assert form_method("POST") == "POST"
    assert form_method(None) is None


def test_form_method_rejects_lowercase() -> None:
    with pytest.raises(ValueError):
        form_method("get")
    with pytest.raises(ValueError):
        Form(method="get")


def test_dbc_form_rejects_novalidate() -> None:
    with pytest.raises(UnsupportedPropError):
        DbcForm(novalidate=True)


def test_input_group_classes_md() -> None:
    assert input_group_classes(size="md") == ["input-group"]


def test_input_group_classes_sm() -> None:
    assert input_group_classes(size="sm") == ["input-group", "input-group-sm"]


def test_input_group_classes_xl_raises() -> None:
    with pytest.raises(ValueError):
        input_group_classes(size="xl")


def test_form_feedback_classes_valid() -> None:
    assert form_feedback_classes(type="valid") == ["valid-feedback"]


def test_form_feedback_classes_invalid_tooltip() -> None:
    assert form_feedback_classes(type="invalid", tooltip=True) == ["invalid-tooltip"]


def test_form_feedback_classes_type_none() -> None:
    assert form_feedback_classes(type=None) == []
    assert form_feedback_classes() == []


def test_form_feedback_type_warning_raises() -> None:
    with pytest.raises(ValueError):
        form_feedback_classes(type="warning")
    with pytest.raises(ValueError):
        FormFeedback(type="warning")


def test_form_text_classes_default() -> None:
    assert form_text_classes() == ["form-text"]


def test_form_text_classes_color() -> None:
    assert form_text_classes(color="muted") == ["form-text", "text-muted"]


def test_surface_identities() -> None:
    assert Form is not DbcForm
    assert form is Form
    assert Form.component_name == "Form"
    assert DbcForm.component_name == "Form"

    assert Label is not DbcLabel
    assert label is Label
    assert Label.component_name == "Label"
    assert DbcLabel.component_name == "Label"

    assert FormText is not DbcFormText
    assert form_text is FormText
    assert FormText.component_name == "FormText"
    assert DbcFormText.component_name == "FormText"

    assert FormFeedback is not DbcFormFeedback
    assert form_feedback is FormFeedback
    assert FormFeedback.component_name == "FormFeedback"
    assert DbcFormFeedback.component_name == "FormFeedback"

    assert FormFloating is not DbcFormFloating
    assert form_floating is FormFloating
    assert FormFloating.component_name == "FormFloating"
    assert DbcFormFloating.component_name == "FormFloating"

    assert InputGroup is not DbcInputGroup
    assert input_group is InputGroup
    assert InputGroup.component_name == "InputGroup"
    assert DbcInputGroup.component_name == "InputGroup"

    assert InputGroupText is not DbcInputGroupText
    assert input_group_text is InputGroupText
    assert InputGroupText.component_name == "InputGroupText"
    assert DbcInputGroupText.component_name == "InputGroupText"


async def test_form_submit_increments_n_submit(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    box: list[Form] = []

    @ui.page("/")
    def page() -> None:
        status = ui.label("submits: 0")

        def on_submit() -> None:
            status.set_text(f"submits: {box[0].n_submit}")

        frm = Form([Button("Submit", type="submit")], on_submit=on_submit)
        box.append(frm)

    await user.open("/")
    await user.should_see("Submit")
    assert box[0].n_submit == 0
    assert box[0]._props.get("data-ngbs-prevent-default") == "true"
    user.find(Form).trigger("submit")
    await user.should_see("submits: 1")
    assert box[0].n_submit == 1


async def test_form_floating_sets_label_html_for(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    labels: list[Label] = []

    @ui.page("/")
    def page() -> None:
        with ui.column():
            lbl = Label("Name")
            FormFloating([ui.element("input"), lbl], html_for="name-field")
            labels.append(lbl)

    await user.open("/")
    assert labels[0]._props.get("for") == "name-field"


async def test_input_group_text_renders(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with InputGroup():
            InputGroupText("kg")

    await user.open("/")
    await user.should_see("kg")
