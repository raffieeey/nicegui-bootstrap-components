"""L2 tests for the alert, spinner, and toast family."""

from __future__ import annotations

import inspect
from typing import Any

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components.bs._alert_spinner import (
    Alert,
    DbcAlert,
    DbcSpinner,
    Spinner,
    alert,
    alert_structural_classes,
    spinner,
    spinner_color_css,
    spinner_fullscreen_classes,
    spinner_is_visible,
    spinner_structural_classes,
)
from nicegui_bootstrap_components.bs._toast import (
    DbcToast,
    Toast,
    toast,
    toast_structural_classes,
)

pytest_plugins = ["nicegui.testing.plugin"]


def test_alert_identity() -> None:
    assert Alert is not DbcAlert
    assert alert is Alert
    assert Alert.component_name == "Alert"
    assert DbcAlert.component_name == "Alert"


def test_spinner_identity() -> None:
    assert Spinner is not DbcSpinner
    assert spinner is Spinner
    assert Spinner.component_name == "Spinner"
    assert DbcSpinner.component_name == "Spinner"


def test_toast_identity() -> None:
    assert Toast is not DbcToast
    assert toast is Toast
    assert Toast.component_name == "Toast"
    assert DbcToast.component_name == "Toast"


def test_alert_structural_classes_default() -> None:
    assert alert_structural_classes(color="primary") == [
        "alert",
        "alert-primary",
        "fade",
        "show",
    ]


def test_alert_structural_classes_dismissable_danger() -> None:
    assert alert_structural_classes(color="danger", dismissable=True) == [
        "alert",
        "alert-danger",
        "alert-dismissible",
        "fade",
        "show",
    ]


def test_alert_structural_classes_closed_fade() -> None:
    assert alert_structural_classes(color="warning", is_open=False) == [
        "alert",
        "alert-warning",
        "fade",
    ]


def test_alert_structural_classes_closed_no_fade() -> None:
    assert alert_structural_classes(color="info", fade=False, is_open=False) == [
        "alert",
        "alert-info",
        "d-none",
    ]


def test_alert_structural_classes_open_no_fade() -> None:
    assert alert_structural_classes(color="success", fade=False) == [
        "alert",
        "alert-success",
    ]


def test_alert_unknown_color_helper() -> None:
    with pytest.raises(ValueError, match="Unknown Alert color"):
        alert_structural_classes(color="chartreuse")


def test_alert_unknown_color_constructor() -> None:
    with pytest.raises(ValueError, match="Unknown Alert color"):
        Alert(color="nope")
    with pytest.raises(ValueError, match="Unknown Alert color"):
        DbcAlert(color="nope")


def test_alert_negative_duration() -> None:
    with pytest.raises(ValueError, match="Alert duration"):
        Alert(duration=-1)


def test_spinner_structural_classes_default() -> None:
    assert spinner_structural_classes() == ["spinner-border"]


def test_spinner_structural_classes_grow_sm_color() -> None:
    assert spinner_structural_classes(type="grow", size="sm", color="primary") == [
        "spinner-grow",
        "spinner-grow-sm",
        "text-primary",
    ]


def test_spinner_hex_color_not_class() -> None:
    assert spinner_structural_classes(color="#ff00aa") == ["spinner-border"]
    assert spinner_color_css("#ff00aa") == "#ff00aa"
    assert spinner_color_css("primary") is None
    assert spinner_color_css(None) is None


def test_spinner_unknown_type() -> None:
    with pytest.raises(ValueError, match="Unknown Spinner type"):
        spinner_structural_classes(type="wheel")
    with pytest.raises(ValueError, match="Unknown Spinner type"):
        Spinner(type="wheel")


def test_spinner_unknown_size() -> None:
    with pytest.raises(ValueError, match="Unknown Spinner size"):
        spinner_structural_classes(size="lg")
    with pytest.raises(ValueError, match="Unknown Spinner size"):
        Spinner(size="lg")


def test_spinner_unknown_display() -> None:
    with pytest.raises(ValueError, match="Unknown Spinner display"):
        spinner_is_visible(display="maybe")
    with pytest.raises(ValueError, match="Unknown Spinner display"):
        Spinner(display="maybe")


def test_spinner_negative_delay() -> None:
    with pytest.raises(ValueError, match="delay_show"):
        Spinner(delay_show=-1)
    with pytest.raises(ValueError, match="delay_hide"):
        Spinner(delay_hide=-5)


def test_spinner_fullscreen_classes() -> None:
    assert spinner_fullscreen_classes() == [
        "position-fixed",
        "top-0",
        "start-0",
        "w-100",
        "h-100",
        "d-flex",
        "align-items-center",
        "justify-content-center",
    ]


@pytest.mark.parametrize(
    ("display", "loading", "has_children", "fullscreen", "expected"),
    [
        ("auto", None, False, False, True),
        ("auto", None, True, False, False),
        ("auto", None, True, True, True),
        ("auto", True, True, False, True),
        ("auto", False, False, False, False),
        ("show", False, False, False, True),
        ("hide", True, False, True, False),
    ],
)
def test_spinner_is_visible_matrix(
    display: str,
    loading: bool | None,
    has_children: bool,
    fullscreen: bool,
    expected: bool,
) -> None:
    assert (
        spinner_is_visible(
            display=display,
            loading=loading,
            has_children=has_children,
            fullscreen=fullscreen,
        )
        is expected
    )


def test_toast_structural_classes() -> None:
    assert toast_structural_classes() == ["toast", "show"]
    assert toast_structural_classes(is_open=True) == ["toast", "show"]
    assert toast_structural_classes(is_open=False) == ["toast"]


def test_toast_has_no_color_prop() -> None:
    assert "color" not in inspect.signature(Toast.__init__).parameters
    assert "color" not in inspect.signature(DbcToast.__init__).parameters


@pytest.mark.user
async def test_alert_renders_and_dismiss_syncs(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    holder: dict[str, Any] = {}

    def on_dismiss() -> None:
        holder["dismissed"] = True

    @ui.page("/")
    def page() -> None:
        component = Alert(
            "Watch out",
            color="warning",
            dismissable=True,
            on_dismiss=on_dismiss,
        )
        holder["component"] = component
        holder["role"] = component._props.get("role")
        holder["classes"] = tuple(component._structural_classes)
        closed = Alert("Hidden", color="danger", is_open=False, fade=False)
        holder["closed_classes"] = tuple(closed._structural_classes)
        none_timer = Alert("Stay", duration=None)
        holder["duration_none"] = none_timer._duration
        timed = Alert("Later", duration=5000)
        holder["duration_ms"] = timed._duration

    await user.open("/")
    await user.should_see("Watch out")
    assert holder["role"] == "alert"
    assert holder["classes"] == (
        "alert",
        "alert-warning",
        "alert-dismissible",
        "fade",
        "show",
    )
    assert holder["closed_classes"] == ("alert", "alert-danger", "d-none")
    assert holder["duration_none"] is None
    assert holder["duration_ms"] == 5000
    component = holder["component"]
    assert component.is_open is True
    component._handle_dismiss()
    assert component.is_open is False
    assert holder.get("dismissed") is True


@pytest.mark.user
async def test_spinner_fullscreen_lifecycle(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    holder: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        plain = Spinner(color="primary", size="sm")
        holder["plain_classes"] = tuple(plain._structural_classes)
        holder["plain_role"] = plain._props.get("role")
        hidden = Spinner(display="hide", loading=True)
        holder["hidden_classes"] = tuple(hidden._structural_classes)
        full = Spinner(fullscreen=True, type="grow")
        holder["full_classes"] = tuple(full._structural_classes)
        holder["full"] = full
        hex_spinner = Spinner(color="#00ffaa")
        holder["hex_classes"] = tuple(hex_spinner._structural_classes)
        holder["hex_style"] = hex_spinner._props.get("style")

    await user.open("/")
    assert holder["plain_classes"] == (
        "spinner-border",
        "spinner-border-sm",
        "text-primary",
    )
    assert holder["plain_role"] == "status"
    assert "d-none" in holder["hidden_classes"]
    assert holder["full_classes"] == tuple(spinner_fullscreen_classes())
    assert holder["hex_classes"] == ("spinner-border",)
    assert holder["hex_style"] == "color: #00ffaa"
    holder["full"].delete()


@pytest.mark.user
async def test_toast_default_open_not_dismissable(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    holder: dict[str, Any] = {}

    @ui.page("/")
    def page() -> None:
        component = Toast("Hello toast", header="Notice")
        holder["role"] = component._props.get("role")
        holder["live"] = component._props.get("aria-live")
        holder["atomic"] = component._props.get("aria-atomic")
        holder["classes"] = tuple(component._structural_classes)
        closed = Toast("Later", is_open=False)
        holder["closed_classes"] = tuple(closed._structural_classes)

    await user.open("/")
    await user.should_see("Hello toast")
    assert holder["role"] == "alert"
    assert holder["live"] == "polite"
    assert holder["atomic"] == "true"
    assert holder["classes"] == ("toast", "show")
    assert holder["closed_classes"] == ("toast",)
