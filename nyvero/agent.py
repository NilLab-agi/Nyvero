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
    show_message, 
    show_tool_call,
    show_header,)

def main():
    show_header()
    user_input = get_input()

    messages = [
        {
            "role": "user",
            "content": user_input,
        }
    ]

    while True:
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

            show_tool_call(
                name, 
                arguments)

            result = execute_tool(
                    name,
                    arguments,
            )

            show_tool_result(result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


if __name__ == "__main__":
    main()
