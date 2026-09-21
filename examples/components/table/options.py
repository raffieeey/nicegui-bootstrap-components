from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    def sample_table(**props) -> None:
        with bs.table(**props):
            with ui.element("thead"), ui.element("tr"):
                ui.html("Name", tag="th")
                ui.html("Role", tag="th")
            with ui.element("tbody"):
                for name, role in (
                    ("Ada", "math"),
                    ("Linus", "kernel"),
                    ("Guido", "language"),
                ):
                    with ui.element("tr"):
                        ui.html(name, tag="td")
                        ui.html(role, tag="td")

    with bs.scope():
        ui.label("Striped and hover")
        sample_table(striped=True, hover=True)
        ui.label("Bordered")
        sample_table(bordered=True, hover=False, striped=False)


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
