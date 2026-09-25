SAFE_TOOLS = {
    "read_file",
    "list_files",
    "file_exists",
    "read_skill",
    "add_todo",
    "list_todos",
    "update_todo",
    "task",
}

CONFIRM_TOOLS = {
    "write_file",
    "edit_file",
    "delete_file",
}

SAFE_BASH_COMMANDS = {
    "pwd",
    "ls",
    "git status",
    "git diff",
    "git log",
    "python --version",
    "python3 --version",
    "pytest",
}

DANGEROUS_BASH_PREFIXES = {
    "sudo ",
    "rm ",
    "rm -",
    "shutdown",
    "reboot",
    "mkfs",
    "dd ",
}

ALLOW = "allow"
CONFIRM = "confirm"
DENY = "deny"


# def requires_confirmation(tool_name, arguments=None):
#     if tool_name in CONFIRM_TOOLS:
#         return CONFIRM

#     if tool_name != "bash":
#         return bash_permission(
#             arguments.get("command", "")
#         )
#     return ALLOW

#     command = arguments.get("command", "").strip()

#     return command not in SAFE_BASH_COMMANDS

def bash_permission(command):
    command = command.strip()

    if command in SAFE_BASH_COMMANDS:
        return ALLOW

    for prefix in DANGEROUS_BASH_PREFIXES:
        if command.startswith(prefix):
            return DENY

    return CONFIRM

def permission_for_tool(tool_name, arguments=None) -> str:
    arguments = arguments or {}

    if tool_name in SAFE_TOOLS:
        return ALLOW

    if tool_name in CONFIRM_TOOLS:
        return CONFIRM

    if tool_name == "bash":
        return bash_permission(
            arguments.get("command", "")
        )

    return DENY