from nicegui import ui

from nicegui_bootstrap_components import StyleMode, bs, setup


def demo() -> None:
    with bs.scope():
        try:
            import pandas as pd
        except ImportError:
            ui.label(
                "Install the examples extra to render this table: "
                "pip install nicegui-bootstrap-components[examples]"
            )
            return
        df = pd.DataFrame(
            {
                "name": ["Ada", "Linus"],
                "role": ["math", "kernel"],
            }
        )
        bs.Table.from_dataframe(
            df,
            index=False,
            striped=True,
            bordered=False,
            hover=True,
            responsive=True,
        )


if __name__ in {"__main__", "__mp_main__"}:
    setup(mode=StyleMode.MIXED)
    demo()
    ui.run()
