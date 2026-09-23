import json

from .llm import (
    stream_llm, 
    collect_stream,
    summarize_messages,
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
    requires_confirmation,
    permission_for_tool,
) 


def main():
    show_header()

    context = Context()

    while True:
        user_input = get_input()

        if user_input.lower() in {"exit", "quit"}:
            show_goodbye()
            break

        context.add_user_message(user_input)
        show_context_status(context.message_count())

        if context.needs_compaction():
            old_messages = context.get_old_messages()

            if old_messages:
                summary = summarize_messages(old_messages)
                context.replace_old_messages(summary)

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
                    tool_result = "Tool excution denied by Nyvero's safety policy"

                    show_error(tool_result)
                    show_tool_result(tool_result)

                    context.add_tool_result(
                        tool_call["id"],
                        tool_result,
                    )

                    continue

                if permission == CONFIRM:
                    if not confirm_tool_call(name,arguments):
                        tool_result = "Tool excution denied by the user"

                        show_tool_result(tool_result)

                        context.add_tool_result(
                            tool_call["id"],
                            tool_result,
                        )
                        
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

if __name__ == "__main__":
    main()
