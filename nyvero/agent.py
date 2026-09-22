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

def main():
    user_input = input("You: ")

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
            print(f"\nNyvero: {message.content}")
            break

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(
                tool_call.function.arguments
            )

            result = execute_tool(
                    name,
                    arguments,
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


if __name__ == "__main__":
    main()
