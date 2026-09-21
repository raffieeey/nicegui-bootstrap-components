from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope(), bs.table(striped=True, bordered=True, hover=True, responsive=True):
        with ui.element("thead"), ui.element("tr"):
            ui.html("Name", tag="th")
            ui.html("Role", tag="th")
            ui.html("Project", tag="th")
        with ui.element("tbody"):
            for name, role, project in (
                ("Ada Lovelace", "Mathematician", "Analytical Engine"),
                ("Linus Torvalds", "Engineer", "Linux"),
                ("Guido van Rossum", "Engineer", "Python"),
            ):
                with ui.element("tr"):
                    ui.html(name, tag="td")
                    ui.html(role, tag="td")
                    ui.html(project, tag="td")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
