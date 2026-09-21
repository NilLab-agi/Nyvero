import subprocess

def bash(command: str) -> str:
    results = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )
    return results.stdout + results.stderr

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

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

READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a text file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read.",
                }
            },
            "required": ["path"],
        },
    },
}

TOOLS =  {
    "bash": bash,
    "read_file": read_file,
}

def execute_tool(name: str, arguments: dict) -> str:
    tool = TOOLS.get(name)

    if tool is None:
        return f"Unknown tool: {name}"

    return tool(**arguments)