"""Kernel-enforced limits on what bash can touch.

One policy - read anything, write only inside the project, no network - with a
different enforcement mechanism per OS.

  Linux   -> bubblewrap, if installed
  macOS   -> the built-in sandbox-exec (seatbelt) profile
  other   -> no OS sandbox available; the command still runs, gated only by
             permissions.py, and the banner reports "none"

Permissions decide what is *allowed*; this decides what is *possible*. They are
independent layers, so a missing sandbox never disables the permission rules.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT = Path.cwd().resolve()

MACOS_PROFILE = f"""(version 1)
(deny default)
(allow process-exec process-fork signal)
(allow file-read*)
(allow sysctl-read)
(deny network*)
(allow file-write* (subpath "{PROJECT}") (literal "/dev/null"))
(deny file-write* (subpath "{PROJECT}/.git"))
"""


def wrap(command: str):
    """Wrap a shell command in an OS sandbox. None means we have no sandbox."""
    if sys.platform == "darwin" and shutil.which("sandbox-exec"):
        profile = Path(tempfile.gettempdir()) / "nyvero.sb"
        profile.write_text(MACOS_PROFILE)
        return ["sandbox-exec", "-f", str(profile), "/bin/sh", "-c", command]

    if shutil.which("bwrap"):
        return [
            "bwrap",
            "--ro-bind", "/", "/",  # normal filesystem is read-only
            "--bind", str(PROJECT), str(PROJECT),  # workspace stays writable
            "--dev", "/dev",
            "--proc", "/proc",
            "--unshare-net",  # no network
            "--die-with-parent",
            "/bin/sh",
            "-c",
            command,
        ]

    return None


def name() -> str:
    """Which mechanism is protecting shell commands right now."""
    if sys.platform == "darwin" and shutil.which("sandbox-exec"):
        return "seatbelt"
    if shutil.which("bwrap"):
        return "bubblewrap"
    return "none"


def run(command: str, timeout: int = 30):
    sandboxed = wrap(command)
    return subprocess.run(
        sandboxed or command,
        shell=sandboxed is None,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
