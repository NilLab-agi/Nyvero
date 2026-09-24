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

from .ui import (
    get_input,
    show_error,
    show_goodbye,
    show_header,
    show_message,
    show_tool_call,
    show_tool_result,
    show_context_status,
    confirm_tool_call,
)

from .context import Context

from .permissions import (
    ALLOW,
    CONFIRM,
    DENY,
    permission_for_tool,
) 

from .import session
from .import compact


# def main():
#     show_header()

#     context = Context()
#     saved_messages = session.load(session.CURRENT)

#     if saved_messages:
#         context.messages = saved_messages

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume the most recent session",
    )

    args = parser.parse_args()

    show_header()

    context = Context()

    if args.resume:
        sessions = session.all_sessions()

        if sessions:
            latest = sessions[0]
            saved_messages = session.open_session(latest["id"])

            if saved_messages:
                context.messages = saved_messages

                print(
                    f"\nResumed session: {latest['title']}"
                )
        else:
            print("\nNo saved sessions found.")

    while True:
        user_input = get_input()

        if user_input.lower() in {"exit", "quit"}:
            show_goodbye()
            break

        context.add_user_message(user_input)
        session.save(context.get_messages())


        show_context_status(context.message_count())

        if context.needs_compaction():
            summary = compact.compact(context.get_messages())

            if summary:
                context.replace_old_messages(summary)
                session.rewrite(context.get_messages())

        # message = call_llm(
        #     messages,
        #     tools=[
        #         BASH_TOOL,
        #         READ_FILE_TOOL,
        #         WRITE_FILE_TOOL,
        #         LIST_FILES_TOOL,
        #         FILE_EXISTS_TOOL,
        #         DELETE_FILE_TOOL,
        #         EDIT_FILE_TOOL,
        #     ],
        # )
        while True:
            print("\nNyvero: ", end="", flush=True)

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
            print()

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
            
            if result["tool_calls"]:
                assistant_message["tool_calls"] = []

                for index, tool_call in enumerate(result["tool_calls"]):
                    assistant_message["tool_calls"].append({
                        "id": tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": tool_call["name"],
                            "arguments": tool_call["arguments"],
                        },
                    })
            context.add_assistant_message(assistant_message)
            session.save(context.get_messages())

            for tool_call in result["tool_calls"]:
                name = tool_call["name"]

                arguments = json.loads(
                    tool_call["arguments"]
                )

                # show_tool_call(
                #     name,
                #     arguments,
                # )

                # try:
                #     tool_result = execute_tool(
                #         name,
                #         arguments,
                #     )
                show_tool_call(
                    name,
                    arguments,
                )

                # if requires_confirmation(name, arguments):
                #     if not confirm_tool_call(name, arguments):
                #         tool_result = "Tool execution denied by the user. "
                #         show_tool_result(tool_result)

                #         context.add_tool_result(
                #             tool_call["id"],
                #             tool_result,
                #         )

                #         continue

                permission = permission_for_tool(
                    name,
                    arguments,
                )

                if permission == DENY:
                    tool_result = "Tool execution denied by Nyvero's safety policy"

                    show_error(tool_result)
                    show_tool_result(tool_result)

                    context.add_tool_result(
                        tool_call["id"],
                        tool_result,
                    )

                    session.save(context.get_messages())

                    continue

                if permission == CONFIRM:
                    if not confirm_tool_call(name,arguments):
                        tool_result = "Tool execution denied by the user"

                        show_tool_result(tool_result)

                        context.add_tool_result(
                            tool_call["id"],
                            tool_result,
                        )

                        session.save(context.get_messages())
                        
                        continue
                    

                try:
                    tool_result = execute_tool(
                        name,
                        arguments,
                    )

                except Exception as error:
                    show_error(str(error))
                    tool_result = f"Tool execution failed: {error}"

                show_tool_result(tool_result)

                context.add_tool_result(
                    tool_call["id"],
                    tool_result,
                 )

                session.save(context.get_messages())

if __name__ == "__main__":
    main()
