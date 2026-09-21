"""Manual and browser-test demo app for both style modes (Mode A and Mode B)."""

from __future__ import annotations

import argparse
import os
from contextlib import nullcontext

from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, dbc, setup
from nicegui_bootstrap_components._host import set_element_text

DARK_WATCHER_HTML = """
<script id="ngbs-dark-watcher">
(function () {
  if (window.__ngbsDarkWatcher) return;
  window.__ngbsDarkWatcher = true;
  const apply = () => {
    const root = document.getElementById('ngbs-overlay-root');
    if (!root) return;
    const dark = document.body.classList.contains('body--dark');
    root.setAttribute('data-bs-theme', dark ? 'dark' : 'light');
  };
  const arm = () => {
    new MutationObserver(apply).observe(document.body, {
      attributes: true,
      attributeFilter: ['class'],
    });
    apply();
  };
  if (document.body) arm();
  else document.addEventListener('DOMContentLoaded', arm);
  setInterval(apply, 250);
})();
</script>
"""


def _resolve_style_mode(mode: str):
    if mode == "unscoped":
        for name in ("UNSCOPED", "BOOTSTRAP_FIRST"):
            if hasattr(StyleMode, name):
                return getattr(StyleMode, name)
        raise AttributeError("StyleMode.UNSCOPED / BOOTSTRAP_FIRST is missing")
    for name in ("MIXED", "SCOPED"):
        if hasattr(StyleMode, name):
            return getattr(StyleMode, name)
    raise AttributeError("StyleMode.MIXED is missing")


def _open_overlay(overlay: object) -> None:
    opener = getattr(overlay, "open", None)
    if callable(opener):
        opener()
        return
    overlay.is_open = True


def _toggle_body_theme() -> None:
    """Flip the Quasar body theme without an app-level toggle binding."""
    ui.run_javascript(
        "document.body.classList.toggle('body--dark');"
        "document.body.classList.toggle('body--light');"
    )


def _modal_title(modal: object, title: str) -> None:
    """dbc-style modal title: <div class=modal-header><h5 class=modal-title>."""
    host = getattr(modal, "_slot_host", None) or modal
    with host, ui.element("div").classes("modal-header"):
        head = ui.element("h5").classes("modal-title")
        head._text = title
        head._props["text"] = title


def _build_island() -> None:
    container = bs.container()
    container.props("id=probe-container")
    with container:
        row = bs.row(class_name="probe-row")
        row.props("id=probe-row")
        with row:
            col = bs.col(xs=12, md=6, class_name="probe-col")
            col.props("id=probe-col")
            with col:
                probe = ui.element("span")
                probe.classes("text-primary")
                probe.props("id=probe-text-primary")
                set_element_text(probe, "Probe")

                status = ui.label("Idle")
                status.props("id=label-status")
                save = bs.button(
                    "Save",
                    color="primary",
                    on_click=lambda: status.set_text("Saved"),
                )
                save.props("id=btn-save")

                name = bs.input(placeholder="Name", debounce=200)
                name.props("id=probe-input")

                bs.button("Hint target", id="probe-tip-target")
                bs.Tooltip("Hello tooltip", target="probe-tip-target", placement="top")

                collapse = bs.Collapse(
                    "Collapsible body",
                    is_open=False,
                    class_name="probe-collapse",
                )
                collapse.props("id=collapse-panel")
                toggle_collapse = bs.button(
                    "Toggle collapse",
                    on_click=collapse.toggle,
                )
                toggle_collapse.props("id=btn-toggle-collapse")

                modal = bs.Modal(
                    "Normal modal body",
                    is_open=False,
                )
                _modal_title(modal, "Normal modal")
                modal_host = getattr(modal, "_slot_host", None) or modal
                with modal_host, ui.element("div").classes("modal-footer"):
                    delete_modal = bs.button("Delete modal", on_click=modal.delete)
                    delete_modal.props("id=btn-delete-modal")
                    toggle_dark_in_modal = ui.button("Toggle dark", on_click=_toggle_body_theme)
                    toggle_dark_in_modal.props("id=btn-toggle-dark-in-modal")
                open_modal = bs.button("Open modal", on_click=modal.open)
                open_modal.props("id=btn-open-modal")
                close_modal = bs.button("Close modal", on_click=modal.close)
                close_modal.props("id=btn-close-modal")
                toggle_modal = bs.button("Toggle modal", on_click=modal.toggle)
                toggle_modal.props("id=btn-toggle-modal")

                static_modal = bs.Modal(
                    "Static modal body",
                    is_open=False,
                    backdrop="static",
                )
                _modal_title(static_modal, "Static modal")
                open_static = bs.button("Open static modal", on_click=static_modal.open)
                open_static.props("id=btn-open-static-modal")

                offcanvas = bs.Offcanvas(
                    "Offcanvas body",
                    is_open=False,
                    placement="end",
                )
                open_offcanvas = bs.button(
                    "Open offcanvas",
                    on_click=lambda: _open_overlay(offcanvas),
                )
                open_offcanvas.props("id=btn-open-offcanvas")

                dropdown_toggle_count = ui.label("Dropdown toggles: 0")
                dropdown_toggle_count.props("id=dropdown-toggle-count")

                def on_dropdown_toggle() -> None:
                    current = int((dropdown_toggle_count.text or "").split(":")[-1].strip())
                    dropdown_toggle_count.set_text(f"Dropdown toggles: {current + 1}")

                dropdown = bs.DropdownMenu(
                    ["Profile", "Logout"],
                    label="Account",
                    direction="down",
                    class_name="probe-dropdown",
                    on_toggle=on_dropdown_toggle,
                )
                dropdown.props("id=probe-dropdown")
                open_dropdown = bs.button(
                    "Open dropdown programmatically",
                    on_click=lambda: setattr(dropdown, "is_open", True),
                )
                open_dropdown.props("id=btn-open-dropdown-programmatically")

                toast_auto = bs.Toast(
                    "autohide body",
                    header="Auto",
                    is_open=False,
                    duration=1000,
                    class_name="probe-toast-auto",
                )
                toast_stay = bs.Toast(
                    "persistent body",
                    header="Stay",
                    is_open=False,
                    class_name="probe-toast-stay",
                )
                show_auto = bs.button(
                    "Show auto toast",
                    on_click=lambda: setattr(toast_auto, "is_open", True),
                )
                show_auto.props("id=btn-toast-auto")
                show_stay = bs.button(
                    "Show stay toast",
                    on_click=lambda: setattr(toast_stay, "is_open", True),
                )
                show_stay.props("id=btn-toast-stay")


def _slice_page(title: str, *, use_scope: bool) -> None:
    dark = ui.dark_mode(False)
    ui.add_head_html(DARK_WATCHER_HTML)
    flag = ui.label(title)
    flag.props("id=mode-flag")
    quasar = ui.button("Quasar contrast")
    quasar.props("id=btn-quasar")
    toggle_dark = ui.button("Toggle dark", on_click=dark.toggle)
    toggle_dark.props("id=btn-toggle-dark")
    with bs.scope() if use_scope else nullcontext():
        _build_island()


def configure_and_register(mode: str) -> None:
    setup(mode=_resolve_style_mode(mode), cdn=False)
    mixed = mode == "mixed"

    @ui.page("/")
    def index() -> None:
        ui.markdown("# ngbs prototype")
        ui.label(f"setup mode: {mode}").props("id=setup-mode")
        ui.link("Mode A", "/mode-a")
        ui.link("Mode B", "/mode-b")
        ui.link("Toasts", "/toasts")
        ui.link("Clicks", "/clicks")
        ui.link("Compat", "/compat")

    @ui.page("/mode-a")
    def mode_a() -> None:
        _slice_page("Mode A", use_scope=False)

    @ui.page("/mode-b")
    def mode_b() -> None:
        _slice_page("Mode B", use_scope=True)

    @ui.page("/light")
    def light() -> None:
        from nicegui_bootstrap_components import ThemeController

        ThemeController.for_client().set_color_mode("light")
        flag = ui.label("light")
        flag.props("id=color-mode-flag")
        _slice_page("Mode B", use_scope=True)

    @ui.page("/dark")
    def dark() -> None:
        from nicegui_bootstrap_components import ThemeController

        ThemeController.for_client().set_color_mode("dark")
        flag = ui.label("dark")
        flag.props("id=color-mode-flag")
        _slice_page("Mode B", use_scope=True)

    @ui.page("/theme")
    def theme_page() -> None:
        from nicegui_bootstrap_components import ThemeController, themes

        controller = ThemeController.for_client()
        controller.set_color_mode("light")
        flag = ui.label("theme page")
        flag.props("id=theme-flag")
        state = ui.label("light")
        state.props("id=theme-state")
        with bs.scope():
            bs.button("Anchor button")

        def choose(mode: str) -> None:
            controller.set_color_mode(mode)
            state.set_text(mode)

        dark_button = bs.button("Set dark", on_click=lambda: choose("dark"))
        dark_button.props("id=btn-theme-dark")
        light_button = bs.button("Set light", on_click=lambda: choose("light"))
        light_button.props("id=btn-theme-light")
        swap = bs.button(
            "Swap to flatly",
            on_click=lambda: controller.set_theme(themes.FLATLY),
        )
        swap.props("id=btn-theme-swap")

    @ui.page("/toasts")
    def toasts() -> None:
        ui.add_head_html(DARK_WATCHER_HTML)
        with bs.scope() if mixed else nullcontext():
            bs.Toast(
                "autohide body",
                header="Auto",
                is_open=True,
                duration=1000,
                class_name="probe-toast-auto",
            )
            bs.Toast(
                "persistent body",
                header="Stay",
                is_open=True,
                class_name="probe-toast-stay",
            )

    @ui.page("/clicks")
    def clicks() -> None:
        ui.add_head_html(DARK_WATCHER_HTML)
        slot: dict[str, object] = {}
        with bs.scope() if mixed else nullcontext():
            count = ui.label("0")
            count.props("id=click-count")

            def on_click() -> None:
                button = slot["button"]
                raw = getattr(button, "n_clicks", None)
                if isinstance(raw, int):
                    count.set_text(str(raw))
                else:
                    count.set_text(str(int(count.text or "0") + 1))

            button = bs.button("Click me", color="primary", on_click=on_click)
            button.props("id=btn-clicks")
            slot["button"] = button

    @ui.page("/compat")
    def compat() -> None:
        ui.add_head_html(DARK_WATCHER_HTML)
        identity = ui.label(str(bs.Button is not dbc.Button))
        identity.props("id=flag-button-identity")
        try:
            dbc.Input(type="color")
        except Exception as exc:
            ui.label(type(exc).__name__).props("id=flag-color-error")
        else:
            ui.label("no-error").props("id=flag-color-error")
        try:
            dbc.Input(debounce=250)
        except Exception as exc:
            ui.label(type(exc).__name__).props("id=flag-debounce-error")
        else:
            ui.label("no-error").props("id=flag-debounce-error")
        try:
            dbc.DropdownMenu(is_open=True)
        except Exception as exc:
            ui.label(type(exc).__name__).props("id=flag-dd-is-open")
        else:
            ui.label("no-error").props("id=flag-dd-is-open")
        with bs.scope() if mixed else nullcontext():
            native_color = bs.input(type="color")
            native_color.props("id=native-color-input")
            native_debounce = bs.input(debounce=250)
            native_debounce.props("id=native-debounce-input")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="ngbs prototype demo")
    parser.add_argument(
        "--mode",
        choices=("mixed", "unscoped"),
        default=os.environ.get("NGBS_PROTOTYPE_MODE", "mixed"),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("NGBS_PROTOTYPE_PORT", "3391")),
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--show", action="store_true")
    args, _unknown = parser.parse_known_args(argv)
    configure_and_register(args.mode)
    print(
        f"ngbs prototype listening on http://{args.host}:{args.port} mode={args.mode}",
        flush=True,
    )
    ui.run(
        reload=False,
        port=args.port,
        host=args.host,
        show=args.show,
        title=f"ngbs prototype ({args.mode})",
        language="en",
    )


if __name__ == "__main__":
    main()
