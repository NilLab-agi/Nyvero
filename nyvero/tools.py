import subprocess

def bash(command: str) -> str:
    results = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    return results.stdout + results.stderr

BASH_TOOL = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a shell command and return its output.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute.",
                }
            },
            "required": ["command"],
        },
    },
}

TOOLS =  {
    "bash": bash
}

def execute_tool(name: str, arguments: dict) -> str:
    tool = TOOLS.get(name)

    if tool is None:
        return f"Unknown tool: {name}"

    return tool(**arguments)