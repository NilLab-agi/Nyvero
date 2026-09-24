import subprocess
from pathlib import Path
from . import sandbox
from .skills import read_skill

from .todos import add_todo, list_todos, update_todo

from .subagent import task

WORKSPACE = Path.cwd().resolve()

def bash(command: str) -> str:
    try:
        result = sandbox.run(command, timeout=30)
    except subprocess.TimeoutExpired:
        return "Command timed out after 30 seconds."

    output = result.stdout + result.stderr

    if result.returncode != 0:
        output += f"\nCommand exited with code {result.returncode}"

    return output


def read_file(path: str) -> str:
    file_path = resolve_workspace_path(path)

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def write_file(path: str, content: str) -> str:
    file_path = resolve_workspace_path(path)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    return f"Successfully wrote to {path}"

# List Tool

def list_files(path: str = ".") -> str:
    directory = resolve_workspace_path(path)

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
    file_path = resolve_workspace_path(path)

    return "true" if file_path.exists() else "false"
    
# delete file tool

def delete_file(path: str) -> str:
    file_path = resolve_workspace_path(path)

    if not file_path.exists():
        return f"Path doesn't exist: {path}"

    if not file_path.is_file():
        return f"Not a file: {path}"
    
    file_path.unlink()

    return f"Succesfully deleted file: {path}"

# Edit file tool

def edit_file(
    path: str,
    old_text: str,
    new_text: str,
) -> str:
    file_path = resolve_workspace_path(path)

    if not file_path.is_file():
        return f"File does not exist: {path}"

    content = file_path.read_text(encoding="utf-8")

    count = content.count(old_text)

    if count == 0:
        return "Edit failed: old_text was not found."

    if count > 1:
        return (
            f"Edit failed: old_text matched {count} times. "
            "Provide more surrounding text to make the match unique."
        )

    updated_content = content.replace(
        old_text,
        new_text,
        1,
    )

    file_path.write_text(
        updated_content,
        encoding="utf-8",
    )

    return f"Successfully edited {path}"

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

READ_SKILL_TOOL = {
    "type": "function",
    "function": {
        "name": "read_skill",
        "description": (
            "Load the full instructions for an available skill. "
            "Use this when a skill is relevant to the current task."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the skill to load."
                },
            },
            "required": ["name"],
        },
        
    }
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

EDIT_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": (
            "Edit an existing text file by replacing one exact, "
            "unique block of text with new text."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the file to edit.",
                },
                "old_text": {
                    "type": "string",
                    "description": (
                        "Exact text currently present in the file. "
                        "It must match exactly once."
                    ),
                },
                "new_text": {
                    "type": "string",
                    "description": (
                        "Replacement text."
                    ),
                },
            },
            "required": [
                "path",
                "old_text",
                "new_text",
            ],
        },
    },
}

ADD_TODO_TOOL = {
    "type": "function",
    "function": {
        "name": "add_todo",
        "description": "Add a new todo item.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The task to add.",
                }
            },
            "required": ["content"],
        },
    },
}

LIST_TODOS_TOOL = {
    "type": "function",
    "function": {
        "name": "list_todos",
        "description": "List all current todo items.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
}

UPDATE_TODO_TOOL = {
    "type": "function",
    "function": {
        "name": "update_todo",
        "description": "Update the status of a todo item.",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_id": {
                    "type": "integer",
                    "description": "The ID of the todo.",
                },
                "status": {
                    "type": "string",
                    "description": "The new status.",
                    "enum": ["pending", "in_progress", "completed"],
                },
            },
            "required": ["todo_id", "status"],
        },
    },
}

TASK_TOOL = {
    "type": "function",
    "function": {
        "name": "task",
        "description": (
            "Delegate a focused read-only exploration task to a fresh "
            "subagent with its own context. The subagent investigates "
            "the codebase and returns a concise report."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "description": {
                    "type": "string",
                    "description": (
                        "A self-contained question or exploration task "
                        "for the subagent."
                    ),
                }
            },
            "required": ["description"],
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
    "edit_file": edit_file,
    "read_skill": read_skill,
    "add_todo": add_todo,
    "list_todo": list_todos,
    "update_todos": update_todo,
    "task": task,
}

def execute_tool(name: str, arguments: dict) -> str:
    tool = TOOLS.get(name)

    if tool is None:
        return f"Unknown tool: {name}"

    return tool(**arguments)


def resolve_workspace_path(path: str) -> Path:
    requested = (WORKSPACE / path).resolve()

    if requested != WORKSPACE and WORKSPACE not in requested.parents:
        raise ValueError(
            f"Path is outside the workspace: {path}"
        )

    return requested

