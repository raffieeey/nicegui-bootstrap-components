"""L2 tests for Stack and ButtonGroup."""

from __future__ import annotations

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, setup
from nicegui_bootstrap_components.bs._actions import (
    Button,
    ButtonGroup,
    DbcButtonGroup,
    button_group,
    button_group_classes,
)
from nicegui_bootstrap_components.bs._layout import DbcStack, Stack, stack, stack_classes

pytest_plugins = ["nicegui.testing.plugin"]
pytestmark = pytest.mark.user


def test_stack_classes() -> None:
    assert stack_classes() == ["vstack"]
    assert stack_classes(direction="horizontal") == ["hstack"]
    assert stack_classes(gap=None) == ["vstack"]
    for n in range(6):
        assert stack_classes(gap=n) == ["vstack", f"gap-{n}"]
    assert stack_classes(direction="horizontal", gap=2) == ["hstack", "gap-2"]
    with pytest.raises(ValueError):
        stack_classes(direction="diagonal")
    with pytest.raises(ValueError):
        stack_classes(gap=True)
    with pytest.raises(ValueError):
        stack_classes(gap=-1)
    with pytest.raises(ValueError):
        stack_classes(gap=6)
    with pytest.raises(ValueError):
        stack_classes(gap="2")
    with pytest.raises(ValueError):
        Stack(direction="diagonal")
    with pytest.raises(ValueError):
        Stack(gap=True)


def test_button_group_classes() -> None:
    assert button_group_classes() == ["btn-group"]
    assert button_group_classes(size="sm") == ["btn-group", "btn-group-sm"]
    assert button_group_classes(size="lg") == ["btn-group", "btn-group-lg"]
    assert button_group_classes(vertical=True) == ["btn-group", "btn-group-vertical"]
    assert button_group_classes(size="sm", vertical=True) == [
        "btn-group",
        "btn-group-sm",
        "btn-group-vertical",
    ]
    assert button_group_classes(size="md") == ["btn-group"]
    with pytest.raises(ValueError):
        button_group_classes(size="xl")
    with pytest.raises(ValueError):
        ButtonGroup(size="xl")


def test_stack_and_button_group_identity() -> None:
    assert Stack is not DbcStack
    assert stack is Stack
    assert Stack.component_name == "Stack"
    assert ButtonGroup is not DbcButtonGroup
    assert button_group is ButtonGroup
    assert ButtonGroup.component_name == "ButtonGroup"


async def test_stack_renders_two_buttons(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with Stack():
            Button("StackOne")
            Button("StackTwo")

    await user.open("/")
    await user.should_see("StackOne")
    await user.should_see("StackTwo")


async def test_button_group_renders_two_buttons(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with ButtonGroup():
            Button("GroupOne")
            Button("GroupTwo")

    await user.open("/")
    await user.should_see("GroupOne")
    await user.should_see("GroupTwo")


async def test_horizontal_stack_renders_label(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        Stack("HorizontalLabel", gap=2, direction="horizontal")

    await user.open("/")
    await user.should_see("HorizontalLabel")
