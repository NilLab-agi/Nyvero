"""Slash commands. Anything typed starting with / lands here.

Keeping these out of agent.py stops the loop from growing a second job: the
loop talks to the model, this file edits the conversation.
"""

from . import session
from .compact import compact
from .ui import ui

COMMANDS = {
    "/compact": "summarise the history so far and free up the context window",
    "/help": "show this list",
}


def handle(command, context):
    if command == "/compact":
        return compact_now(context)

    # /help, or anything else that starts with /.
    ui.agent(
        "Commands:\n\n"
        + "\n".join(
            f"- `{name}` — {help}" for name, help in COMMANDS.items()
        )
    )
    return context


def compact_now(context):
    before = context.message_count()

    with ui.working("compacting"):
        summary = compact(context.get_messages())

    if not summary:
        ui.agent("Nothing old enough to compact yet.")
        return context

    context.replace_old_messages(summary)
    session.rewrite(context.get_messages())
    ui.compacted(before, context.message_count())
    return context
