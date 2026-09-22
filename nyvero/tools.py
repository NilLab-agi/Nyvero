import subprocess
from pathlib import Path

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

def write_file(path: str, content: str) -> str:
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    return f"Successfully wrote to {path}"

# List Tool

def list_files(path: str = ".") -> str:
    directory = Path(path)

    if not directory.is_dir():
        return f"Not a directory: {path}"

    entries = sorted(directory.iterdir())

    if not entries:
        return "(empty directory)"

    return "\n".join(
        f"{'[DIR] ' if entry.is_dir() else '[FILE]' }{entry.name}" for entry in entries
    )
    
# file_exists tool — check whether a path exists

def file_exists(path: str) -> str:
    return "true" if Path(path).exists() else "false"
    
# delete file tool

def delete_file(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        return f"Path doesn't exist: {path}"

    if file_path.is_file():
        return f"Not a file: {path}"
    
    file_path.unlink()

    return f"Succesfully deleted file: {path}"


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

WRITE_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content to a file, replacing the file if it already exists",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Complete content to write to the file",
                }
            },
            "required": ["path", "content"],
        }
    }
}

LIST_FILES_TOOL = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List files and directories inside a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path to list. Defaults to the current directory.",
                }
            },
            "required": [],
        },
    },
}

FILE_EXISTS_TOOL = {
    "type": "function",
    "function": {
        "name": "file_exists",
        "description": "Check whether a file or directory exists at the given path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check.",
                }
            },
            "required": ["path"],
        },
    },
}

DELETE_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "delete_file",
        "description": "Delete a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the file to delete.",
                }
            },
            "required": ["path"],
        },
    },
}

TOOLS =  {
    "bash": bash,
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "file_exists": file_exists,
    "delete_file": delete_file, 
}

def execute_tool(name: str, arguments: dict) -> str:
    tool = TOOLS.get(name)

    if tool is None:
        return f"Unknown tool: {name}"

    return tool(**arguments)


