import json
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path.home() / ".nyvero" / "sessions"

CURRENT = datetime.now().strftime("%Y%m%d-%H%M%S") 

# Every Nyvero run gets a session identifier such as:
# ~/.nyvero/sessions/20260923-072500.jsonl 

WRITTEN = 0

def path_for(session_id:str) -> Path:
    return SESSION_DIR / f"{session_id}.jsonl"

# If we call:

# path_for("20260923-072500")

# Python constructs:

# ~/.nyvero/sessions/20260923-072500.jsonl

# We're deliberately using .jsonl, not .json.

def save(messages):
    global WRITTEN

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    with path_for(CURRENT).open("a", encoding="utf-8") as file:
        for message in messages[WRITTEN:]:
            file.write(json.dumps(message) + "\n")
    
    WRITTEN = len(message)
# rather than rewriting the entire conversation every time.
# That gives us an append-only transcript

def load(session_id: str):
    messages = []

    session_path = path_for(session_id)

    if not session_path.exists():
        return messages

    for line in session_path.read_text(encoding="utf-8").splitlines():
        if not line.split():
            continue

        try:
            messages.append(json.loads(line))
        except json.JSONDecodeError:
            continue

        return messages
    # Load a saved session

    