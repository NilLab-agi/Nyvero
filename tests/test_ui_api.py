"""Every ui.<method> called anywhere in the package must exist on UI.

This guards the class of bug where agent.py calls a UI method that was never
defined (e.g. ui.resumed / ui.note), which crashed `nyvero --resume` at runtime.
"""

import re
from pathlib import Path

from nyvero.ui import UI

PKG = Path(__file__).resolve().parent.parent / "nyvero"


def test_every_ui_call_exists():
    defined = {name for name in dir(UI) if not name.startswith("__")}
    called = set()
    for path in PKG.glob("*.py"):
        called |= set(re.findall(r"\bui\.([a-zA-Z_]\w*)", path.read_text()))

    missing = called - defined
    assert not missing, f"ui methods called but not defined: {sorted(missing)}"
