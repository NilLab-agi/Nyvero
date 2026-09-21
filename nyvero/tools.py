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