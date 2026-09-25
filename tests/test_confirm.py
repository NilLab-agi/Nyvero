"""Confirmation gate: blank input re-prompts, y/n decides, EOF denies."""

import builtins

from nyvero.ui import UI


def answer(*replies):
    replies = iter(replies)
    builtins.input = lambda prompt: next(replies)


def test_confirm():
    ui = UI()
    answer("", "maybe", "yes")
    assert ui.confirm("write_file", {"path": "x.py"}) is True

    answer("n")
    assert ui.confirm("write_file", {"path": "x.py"}) is False

    answer("", "", "no")
    assert ui.confirm("write_file", {"path": "x.py"}) is False


def test_confirm_eof_denies():
    def eof(prompt):
        raise EOFError

    builtins.input = eof
    assert UI().confirm("write_file", {"path": "x.py"}) is False
