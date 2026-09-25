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


def test_nicegui_dependency_allows_future_minor_but_not_major() -> None:
    from pathlib import Path

    import tomllib
    from packaging.requirements import Requirement

    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    dependencies = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["dependencies"]
    nicegui = [Requirement(dep) for dep in dependencies if Requirement(dep).name == "nicegui"]

    assert len(nicegui) == 1
    assert "3.17.1" in nicegui[0].specifier
    assert "3.18.0" in nicegui[0].specifier
    assert "4.0.0" not in nicegui[0].specifier
