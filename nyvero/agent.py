import json

from .llm import stream_llm, collect_stream
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
            messages.append(assistant_message)

            for tool_call in result["tool_calls"]:
                name = tool_call["name"]

                arguments = json.loads(
                    tool_call["arguments"]
                )

                show_tool_call(
                    name,
                    arguments,
                )

                try:
                    tool_result = execute_tool(
                        name,
                        arguments,
                    )
                except Exception as error:
                    show_error(str(error))
                    tool_result = f"Tool execution failed: {error}"

                show_tool_result(tool_result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result,
                })


if __name__ == "__main__":
    main()
