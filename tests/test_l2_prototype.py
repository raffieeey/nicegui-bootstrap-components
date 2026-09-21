from collections.abc import Callable

import pytest
from nicegui import ui
from nicegui.testing import User

from nicegui_bootstrap_components import StyleMode, bs, setup

pytest_plugins = ["nicegui.testing.plugin"]
pytestmark = pytest.mark.user


async def test_button_click_updates_label(user: User) -> None:
    setup(mode=StyleMode.MIXED)

    @ui.page("/")
    def page() -> None:
        with bs.scope():
            status = ui.label("Idle")
            bs.button("Apply", on_click=lambda: status.set_text("Applied"))

    await user.open("/")
    user.find("Apply").click()
    await user.should_see("Applied")


async def test_two_clients_independent(user: User, create_user: Callable[[], User]) -> None:
    setup(mode=StyleMode.MIXED)
    buttons: list = []
    inputs: list = []

    @ui.page("/")
    def page() -> None:
        with bs.scope():
            click_label = ui.label("clicks: 0")
            btn = bs.button(
                "Tap",
                color="primary",
                on_click=lambda: click_label.set_text(f"clicks: {btn.n_clicks}"),
            )
            buttons.append(btn)
            field = bs.input(value="start")
            inputs.append(field)
            value_label = ui.label("start")

            def change_value() -> None:
                field.value = "changed"
                value_label.set_text(str(field.value))

            bs.button("Change", on_click=change_value)

    user_a = user
    user_b = create_user()
    await user_a.open("/")
    await user_b.open("/")

    await user_a.should_see("clicks: 0")
    await user_b.should_see("clicks: 0")
    user_a.find("Tap").click()
    await user_a.should_see("clicks: 1")
    await user_b.should_see("clicks: 0")
    await user_b.should_not_see("clicks: 1")
    assert buttons[0] is not buttons[1]
    assert buttons[1].n_clicks == 0

    await user_a.should_see("start")
    await user_b.should_see("start")
    user_a.find("Change").click()
    await user_a.should_see("changed")
    await user_b.should_see("start")
    await user_b.should_not_see("changed")
    assert inputs[0] is not inputs[1]
    assert inputs[0].value == "changed"
    assert inputs[1].value == "start"


async def test_input_value_round_trip(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    box: list = []

    @ui.page("/")
    def page() -> None:
        with bs.scope():
            inp = bs.input(value="hello", placeholder="Name")
            box.append(inp)
            ui.label().bind_text_from(inp, "value")

    await user.open("/")
    inp = box[0]
    assert inp.value == "hello"
    await user.should_see("hello")
    inp.value = "world"
    assert inp.value == "world"
    await user.should_see("world")


async def test_modal_open_close_via_python_callbacks(user: User) -> None:
    setup(mode=StyleMode.MIXED)
    box: list = []

    @ui.page("/")
    def page() -> None:
        with bs.scope():
            flag = ui.label("modal:closed")
            modal = bs.modal(is_open=False)
            box.append(modal)

            def open_modal() -> None:
                modal.is_open = True
                flag.set_text("modal:open")

            def close_modal() -> None:
                modal.is_open = False
                flag.set_text("modal:closed")

            bs.button("Open modal", on_click=open_modal)
            bs.button("Close modal", on_click=close_modal)

    await user.open("/")
    modal = box[0]
    assert modal.is_open is False
    await user.should_see("modal:closed")
    user.find("Open modal").click()
    assert modal.is_open is True
    await user.should_see("modal:open")
    user.find("Close modal").click()
    assert modal.is_open is False
    await user.should_see("modal:closed")
