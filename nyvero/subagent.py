import json

from .llm import (
    stream_llm,
    collect_stream,
)
# from .tools import (
#     BASH_TOOL,
#     READ_FILE_TOOL,
#     LIST_FILES_TOOL,
#     FILE_EXISTS_TOOL,
#     READ_SKILL_TOOL,
#     execute_tool,
# )

def get_subagent_tools():
    from .tools import (
        BASH_TOOL,
        READ_FILE_TOOL,
        LIST_FILES_TOOL,
        FILE_EXISTS_TOOL,
        READ_SKILL_TOOL,
    )

    return [
        BASH_TOOL,
        READ_FILE_TOOL,
        LIST_FILES_TOOL,
        FILE_EXISTS_TOOL,
        READ_SKILL_TOOL,
    ]


MAX_TURNS = 12


SUBAGENT_SYSTEM_PROMPT = """
You are a Nyvero exploration subagent.

Your job is to investigate the codebase and report your findings
to the main agent.

You have your own isolated context and cannot see the main agent's
conversation.

You are READ-ONLY.

You may:
- inspect files
- search the codebase
- inspect directories
- check whether files exist
- read available skills

You must NOT:
- create files
- modify files
- delete files
- edit files
- create todos
- modify the main agent's plan
- call another subagent

Search the current project directory only.

Prefer targeted searches over scanning the entire filesystem.

Stop when you have enough information to answer the question.

Your final response should be a concise report containing:
- what you found
- relevant file paths
- relevant functions/classes when useful
- important relationships between components

Do not guess. If you cannot find something, say so clearly.
""".strip()


# SUBAGENT_TOOLS = [
#     BASH_TOOL,
#     READ_FILE_TOOL,
#     LIST_FILES_TOOL,
#     FILE_EXISTS_TOOL,
#     READ_SKILL_TOOL,
# ]


ALLOWED_TOOLS = {
    "bash",
    "read_file",
    "list_files",
    "file_exists",
    "read_skill",
}


def task(description: str) -> str:
    """
    Run an isolated read-only exploration agent.

    The subagent receives only the task description and returns
    its final textual findings to the parent agent.
    """
    from .tools import execute_tool

    messages = [
        {
            "role": "system",
            "content": SUBAGENT_SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": description,
        },
    ]

    last_report = None

    for _ in range(MAX_TURNS):
        stream = stream_llm(
            messages,
            tools=get_subagent_tools(),
        )

        result = collect_stream(stream)

        if result["content"]:
            last_report = result["content"]

        if not result["tool_calls"]:
            return result["content"] or last_report or (
                "The subagent completed without producing a report."
            )

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

        messages.append(assistant_message)

        for tool_call in result["tool_calls"]:
            name = tool_call["name"]

            if name not in ALLOWED_TOOLS:
                tool_result = (
                    f"Tool '{name}' is not available to the subagent."
                )
            else:
                try:
                    arguments = json.loads(tool_call["arguments"])
                    tool_result = execute_tool(name, arguments)
                except Exception as error:
                    tool_result = f"Tool execution failed: {error}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": tool_result,
            })

    if last_report:
        return (
            f"(Subagent stopped after {MAX_TURNS} turns.)\n\n"
            f"{last_report}"
        )

    return (
        f"Subagent stopped after {MAX_TURNS} turns "
        "without producing a report."
    )