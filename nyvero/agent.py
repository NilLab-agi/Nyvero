import argparse
import json

from .llm import (
    stream_llm,
    collect_stream,
)

from .tools import (
    BASH_TOOL,
    READ_FILE_TOOL,
    WRITE_FILE_TOOL,
    LIST_FILES_TOOL,
    FILE_EXISTS_TOOL,
    DELETE_FILE_TOOL,
    EDIT_FILE_TOOL,
    execute_tool,
    READ_SKILL_TOOL,
    ADD_TODO_TOOL,
    LIST_TODOS_TOOL,
    UPDATE_TODO_TOOL,
    TASK_TOOL,
)

from .ui import ui
from .context import Context

from .permissions import (
    CONFIRM,
    DENY,
    permission_for_tool,
)

from . import session
from . import compact


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume the most recent session",
    )

    args = parser.parse_args()

    ui.banner()

    context = Context()

    if args.resume:
        sessions = session.all_sessions()

        if sessions:
            latest = sessions[0]
            saved_messages = session.open_session(latest["id"])

            if saved_messages:
                context.messages = saved_messages
                ui.resumed(
                    context.get_messages(),
                    latest["title"],
                )
        else:
            ui.note("No saved sessions found.")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            ui.goodbye()
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            ui.goodbye()
            break

        ui.user(user_input)

        context.add_user_message(user_input)
        session.save(context.get_messages())

        ui.context_status(context.message_count())

        if context.needs_compaction():
            summary = compact.compact(
                context.get_messages()
            )

            if summary:
                before = context.message_count()

                context.replace_old_messages(summary)
                session.rewrite(
                    context.get_messages()
                )

                ui.compacted(
                    before,
                    context.get_messages(),
                )

        while True:
            with ui.working("thinking"):
                stream = stream_llm(
                    context.get_messages(),
                    tools=[
                        BASH_TOOL,
                        READ_FILE_TOOL,
                        WRITE_FILE_TOOL,
                        LIST_FILES_TOOL,
                        FILE_EXISTS_TOOL,
                        DELETE_FILE_TOOL,
                        EDIT_FILE_TOOL,
                        READ_SKILL_TOOL,
                        ADD_TODO_TOOL,
                        LIST_TODOS_TOOL,
                        UPDATE_TODO_TOOL,
                        TASK_TOOL,
                    ],
                )

                result = collect_stream(stream)

            if result["content"]:
                ui.agent(result["content"])

            if not result["tool_calls"]:
                break

            assistant_message = {
                "role": "assistant",
                "content": result["content"],
            }

            if result["reasoning_content"]:
                assistant_message["reasoning_content"] = (
                    result["reasoning_content"]
                )

            assistant_message["tool_calls"] = []

            for tool_call in result["tool_calls"]:
                assistant_message["tool_calls"].append({
                    "id": tool_call["id"],
                    "type": "function",
                    "function": {
                        "name": tool_call["name"],
                        "arguments": tool_call["arguments"],
                    },
                })

            context.add_assistant_message(
                assistant_message
            )

            session.save(
                context.get_messages()
            )

            for tool_call in result["tool_calls"]:
                name = tool_call["name"]

                arguments = json.loads(
                    tool_call["arguments"]
                )

                ui.tool_call(
                    name,
                    arguments,
                )

                permission = permission_for_tool(
                    name,
                    arguments,
                )

                if permission == DENY:
                    tool_result = (
                        "Tool execution denied by "
                        "Nyvero's safety policy"
                    )

                    ui.error(tool_result)

                    ui.tool(
                        name,
                        arguments,
                        tool_result,
                    )

                    context.add_tool_result(
                        tool_call["id"],
                        tool_result,
                    )

                    session.save(
                        context.get_messages()
                    )

                    continue

                if permission == CONFIRM:
                    if not ui.confirm(
                        name,
                        arguments,
                    ):
                        tool_result = (
                            "Tool execution denied "
                            "by the user"
                        )

                        ui.tool(
                            name,
                            arguments,
                            tool_result,
                        )

                        context.add_tool_result(
                            tool_call["id"],
                            tool_result,
                        )

                        session.save(
                            context.get_messages()
                        )

                        continue

                try:
                    tool_result = execute_tool(
                        name,
                        arguments,
                    )

                except Exception as error:
                    ui.error(str(error))

                    tool_result = (
                        f"Tool execution failed: {error}"
                    )

                ui.tool(
                    name,
                    arguments,
                    tool_result,
                )

                context.add_tool_result(
                    tool_call["id"],
                    tool_result,
                )

                session.save(
                    context.get_messages()
                )


if __name__ == "__main__":
    main()