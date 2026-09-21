from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope(), bs.card_group():
        with bs.card():
            bs.card_img(
                src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='140'%3E%3Crect width='400' height='140' fill='%230d6efd'/%3E%3Ctext x='200' y='80' text-anchor='middle' fill='%23fff' font-family='sans-serif' font-size='22'%3EQ3%3C/text%3E%3C/svg%3E",
                alt="Q3 revenue chart",
                top=True,
            )
            bs.card_header("Quarterly report")
            with bs.card_body():
                ui.label("Revenue was up 12% versus last quarter.")
                bs.card_link("Open workbook", href="/reports/q3")
            bs.card_footer("Updated today")
        with bs.card():
            bs.card_header("Headcount")
            with bs.card_body():
                ui.label("Fourteen people joined the platform team.")
            bs.card_footer("HR snapshot")


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run(title="Card group composition")
