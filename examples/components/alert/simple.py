"""Alerts in every contextual color."""

from nicegui import ui

from nicegui_bootstrap_components import bs


def demo() -> None:
    with bs.scope():
        bs.alert("This is a primary alert", color="primary")
        bs.alert("This is a secondary alert", color="secondary")
        bs.alert("This is a success alert! Well done!", color="success")
        bs.alert("This is a warning alert... be careful...", color="warning")
        bs.alert("This is a danger alert. Scary!", color="danger")
        bs.alert("This is an info alert. Good to know!", color="info")
        bs.alert("This is a light alert", color="light")
        bs.alert("This is a dark alert", color="dark")


if __name__ in {"__main__", "__mp_main__"}:
    demo()
    ui.run(title="Alerts")
