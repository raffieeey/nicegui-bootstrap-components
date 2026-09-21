def test_package_imports() -> None:
    import nicegui_bootstrap_components as nbc

    assert hasattr(nbc, "bs")
    assert hasattr(nbc, "dbc")


def test_namespaces_importable() -> None:
    from nicegui_bootstrap_components import bs, dbc

    assert bs.__doc__ is not None
    assert dbc.__doc__ is not None


def test_package_version_matches_pyproject() -> None:
    from pathlib import Path

    import tomllib

    import nicegui_bootstrap_components as nbc

    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    declared = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
    assert nbc.__version__ == declared, (
        f"package __version__ ({nbc.__version__}) must match pyproject version ({declared})"
    )
