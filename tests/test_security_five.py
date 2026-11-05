"""Regression tests for the five confirmed security and correctness issues."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing import User
from scripts.build_styles import scope_css, strip_remote_imports

from nicegui_bootstrap_components.bs._actions import Button
from nicegui_bootstrap_components.bs._alert_spinner import Alert
from nicegui_bootstrap_components.bs._carousel import Carousel
from nicegui_bootstrap_components.bs._content import ListGroupItem
from nicegui_bootstrap_components.bs._inputs import Input, Textarea
from nicegui_bootstrap_components.bs._nav import Breadcrumb, NavLink
from nicegui_bootstrap_components.bs._overlays import Accordion
from nicegui_bootstrap_components.bs._tabs import DbcTabs, Tabs

pytest_plugins = ["nicegui.testing.plugin"]
PAYLOAD = '/path with "quotes" [x] :evil=alert(1)'
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.user
async def test_f01_button_attrs_are_atomic(user: User) -> None:
    holder = {}

    @ui.page("/")
    def page() -> None:
        holder["button"] = Button(
            "Link", href=PAYLOAD, name=PAYLOAD, value=PAYLOAD, external_link=True
        )
        holder["download"] = Button("Download", href="/x", download=True)
        holder["omitted"] = Button("No attrs", href="/x", download=False, name="", value="")
        holder["disabled"] = Button("Disabled", disabled=True)

    await user.open("/")
    props = holder["button"]._props
    for key in ("href", "name", "value"):
        assert props[key] == PAYLOAD
    assert props["rel"] == "noopener noreferrer"
    assert ":evil" not in props and "noreferrer" not in props
    assert holder["download"]._props["download"] is True
    assert holder["disabled"]._props["disabled"] is True
    assert not {"download", "name", "value", "target", "rel"} & holder["omitted"]._props.keys()


@pytest.mark.user
async def test_f01_nav_and_breadcrumb_attrs_are_atomic(user: User) -> None:
    holder = {}

    @ui.page("/")
    def page() -> None:
        holder["nav"] = NavLink("Link", href=PAYLOAD, external_link=True)
        holder["crumb"] = Breadcrumb(
            items=[{"label": "link", "href": PAYLOAD, "title": PAYLOAD, "external_link": True}]
        )

    await user.open("/")
    nav = holder["nav"]._props
    li = holder["crumb"]._list.default_slot.children[0]
    anchor = li.default_slot.children[0]._props
    for props in (nav, anchor):
        assert props["href"] == PAYLOAD
        assert props["rel"] == "noopener noreferrer"
        assert ":evil" not in props and "noreferrer" not in props
    assert anchor["title"] == PAYLOAD


@pytest.mark.user
async def test_f02_disabled_click_does_not_fire(user: User) -> None:
    holder = {}
    calls = []

    @ui.page("/")
    def page() -> None:
        holder["disabled"] = ListGroupItem(
            "No", disabled=True, n_clicks=4, on_click=lambda: calls.append("no")
        )
        holder["enabled"] = ListGroupItem("Yes", on_click=lambda: calls.append("yes"))

    await user.open("/")
    holder["disabled"]._handle_click()
    assert holder["disabled"]._n_clicks == 4 and calls == []
    holder["enabled"]._handle_click()
    assert holder["enabled"]._n_clicks == 1 and calls == ["yes"]


@pytest.mark.parametrize("mode", ["local", "session"])
@pytest.mark.parametrize(
    "factory",
    [
        lambda mode: Input(id="test", persist=mode),
        lambda mode: Textarea(id="test", persist=mode),
        lambda mode: Carousel(items=[], id="test", persist=mode),
        lambda mode: Accordion(id="test", persist=mode),
        lambda mode: Tabs(id="test", persist=mode),
    ],
)
@pytest.mark.user
async def test_f03_unsupported_persistence_fails_closed(factory, mode: str, user: User) -> None:
    result = []

    @ui.page("/")
    def page() -> None:
        try:
            factory(mode)
        except NotImplementedError as exc:
            result.append(str(exc))

    await user.open("/")
    assert result and "persist" in result[0]


@pytest.mark.parametrize("mode", ["local", "session", "memory"])
@pytest.mark.user
async def test_f03_compat_persistence_fails_closed(mode: str, user: User) -> None:
    result = []

    @ui.page("/")
    def page() -> None:
        try:
            DbcTabs(id="test", persistence=True, persistence_type=mode)
        except NotImplementedError as exc:
            result.append(str(exc))

    await user.open("/")
    assert result and "persist" in result[0]


def test_f04_scope_transform_removes_remote_import() -> None:
    source = '/* license */\n@import url("https://fonts.example/font.css");\nbody { color: red; }'
    result = scope_css(source)
    assert "/* license */" in result and ".ngbs { color: red; }" in result
    assert "@import" not in result and "fonts.example" not in result


def test_f04_import_transform_preserves_local_import_and_bytes() -> None:
    source = (
        '/* license */\n@import "local.css";\n'
        '@import url("https://example.test/a;b.css");\n'
        "@import '//example.test/second.css' screen;\n"
        'a { content: "unchanged"; }\n'
    )
    assert strip_remote_imports(source) == (
        '/* license */\n@import "local.css";\n\n\na { content: "unchanged"; }\n'
    )


def test_f04_all_committed_css_offline_and_identical() -> None:
    dirs = (ROOT / "styles/dist", ROOT / "src/nicegui_bootstrap_components/static/dist")
    files = sorted(dirs[0].glob("*.css"))
    assert files and {p.name for p in files} == {p.name for p in dirs[1].glob("*.css")}
    for path in files:
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        assert not re.search(r'@import\s+(?:url\()?\s*[\'"]?(?:https?:)?//', text, re.I), path
        assert path.read_bytes() == (dirs[1] / path.name).read_bytes()


@pytest.mark.parametrize("fade", [True, False])
@pytest.mark.user
async def test_f05_dismiss_hide_reopen_and_timer(user: User, fade: bool) -> None:
    holder = {}
    calls = []

    @ui.page("/")
    def page() -> None:
        holder["alert"] = Alert(
            "Alert", fade=fade, duration=5000, on_dismiss=lambda: calls.append("dismissed")
        )
        holder["closed"] = Alert("Hidden", fade=fade, is_open=False)

    await user.open("/")
    alert = holder["alert"]
    assert "d-none" in holder["closed"]._classes
    timer = alert._timer
    assert timer is not None
    alert._handle_dismiss()
    assert not alert.is_open and "d-none" in alert._classes and alert._timer is None
    assert calls == ["dismissed"]
    alert._handle_dismiss()
    assert calls == ["dismissed"]
    with alert:
        alert.is_open = True
    assert alert.is_open and "d-none" not in alert._classes and alert._timer is not None
    if fade:
        assert "show" in alert._classes
    alert._handle_dismiss()
