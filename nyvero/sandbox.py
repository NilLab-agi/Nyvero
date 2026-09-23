import shutil
import subprocess
from pathlib import Path

PROJECT = Path.cwd().resolve()

def wrap(command: str):
    if not shutil.which("bwrap"):
        return None
    
    return [
        "bwrap", 
        "--ro-bind", "/", "/", # The normal filesystem is exposed read-only
        "--bind", str(PROJECT), str(PROJECT), # makes Nyvero workspace writable
        "--dev", "/dev",
        "--proc", "/proc",
        "--unshare-net", # removes network access from the sandboxed command
        "--die-with-parent", # makes the sandbox process terminate with Nyvero's process
        "/bin/sh",
        "-c",
        command,
    ]

def run(command: str, timeout: int =30):
    sandboxed_command = wrap(command)

    if sandboxed_command is None:
        raise RuntimeError("Bubblewrap is not available.")
    try:
        return subprocess.run(
            sandboxed_command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise