"""Navbar fixed and sticky placement."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.navbar_simple(brand="Fixed top", color="dark", dark=True, fixed="top")
        with bs.container():
            ui.label("Fixed navbar sits at the viewport top.")
            for index in range(10):
                ui.label(f"Fixed section {index + 1}")
        bs.navbar_simple(brand="Sticky top", color="primary", dark=True, sticky="top")
        with bs.container():
            ui.label("Sticky navbar remains at the top while this section scrolls.")
            for index in range(16):
                ui.label(f"Sticky section {index + 1}")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Navbar fixed and sticky")
