"""Modal with a static backdrop."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        modal = bs.modal(is_open=False, backdrop="static")
        with modal:
            ui.label("Clicking the backdrop does not close this modal.")

            def close_modal() -> None:
                modal.set_value(False)

            bs.button("Close", on_click=close_modal)

        def open_modal() -> None:
            modal.set_value(True)

        bs.button("Open modal", on_click=open_modal)


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Static backdrop modal")
