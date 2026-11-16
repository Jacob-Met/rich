import io
import os
import tempfile

import pytest

from rich.console import Console
from rich.style import Style
from rich.theme import Theme, ThemeStack, ThemeStackError


def test_inherit():
    theme = Theme({"warning": "red"})
    assert theme.styles["warning"] == Style(color="red")
    assert theme.styles["dim"] == Style(dim=True)


def test_config():
    theme = Theme({"warning": "red"})
    config = theme.config
    assert "warning = red\n" in config


def test_from_file():
    theme = Theme({"warning": "red"})
    text_file = io.StringIO()
    text_file.write(theme.config)
    text_file.seek(0)

    load_theme = Theme.from_file(text_file)
    assert theme.styles == load_theme.styles


def test_read():
    theme = Theme({"warning": "red"})
    with tempfile.TemporaryDirectory("richtheme") as name:
        filename = os.path.join(name, "theme.cfg")
        with open(filename, "wt") as write_theme:
            write_theme.write(theme.config)
        load_theme = Theme.read(filename)
        assert theme.styles == load_theme.styles


def test_theme_stack():
    theme = Theme({"warning": "red"})
    stack = ThemeStack(theme)
    assert stack.get("warning") == Style.parse("red")
    new_theme = Theme({"warning": "bold yellow"})
    stack.push_theme(new_theme)
    assert stack.get("warning") == Style.parse("bold yellow")
    stack.pop_theme()
    assert stack.get("warning") == Style.parse("red")
    with pytest.raises(ThemeStackError):
        stack.pop_theme()


def test_use_theme_respects_inherit_false() -> None:
    output = io.StringIO()
    console = Console(file=output, force_terminal=True, color_system="truecolor")
    theme = Theme({"warning": "red"}, inherit=False)

    def render() -> str:
        output.seek(0)
        output.truncate(0)
        console.print("[warning]warning[/] 42", end="")
        return output.getvalue()

    console.push_theme(theme, inherit=False)
    without_inheritance = render()
    console.pop_theme()

    with console.use_theme(theme, inherit=False):
        assert render() == without_inheritance

    with console.use_theme(theme, inherit=True):
        assert render() != without_inheritance
