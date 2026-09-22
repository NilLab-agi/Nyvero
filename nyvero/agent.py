import json

from .llm import call_llm
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
)


def main():
    show_header()

    messages = []

    while True:
        user_input = get_input()

        if user_input.lower() in {"exit", "quit"}:
            show_goodbye()
            break

        messages.append({
            "role": "user",
            "content": user_input,
        })

        message = call_llm(
            messages,
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

        messages.append(
            message.model_dump(exclude_none=True)
        )

        if not message.tool_calls:
            show_message(f"{message.content}")
            break

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(
                tool_call.function.arguments
            )

            show_tool_call(name, arguments)
            try:
                result = execute_tool(
                    name,
                    arguments,
                )
            except Exception as errors:
                show_error(str(errors))
                result = f"Tool execution failed: {errors}"

            show_tool_result(result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


if __name__ == "__main__":
    main()
