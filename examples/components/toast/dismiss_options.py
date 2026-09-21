"""Toast dismissable and duration options."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():

        def show_dismissable() -> None:
            bs.toast(
                "Saved",
                duration=3000,
                dismissable=True,
                class_name="position-fixed top-0 end-0 m-3",
            )

        def show_timed() -> None:
            bs.toast(
                "Auto-hide",
                duration=2000,
                dismissable=False,
                class_name="position-fixed top-0 end-0 m-3",
            )

        bs.button("Dismissable, 3s", on_click=show_dismissable)
        bs.button("Not dismissable, 2s", on_click=show_timed)


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Toast dismiss options")
