SAFE_TOOLS = {
    "read_file",
    "list_files",
    "file_exists",
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


def requires_confirmation(tool_name, arguments=None):
    if tool_name in CONFIRM_TOOLS:
        return True

    if tool_name != "bash":
        return False

    command = arguments.get("command", "").strip()

    return command not in SAFE_BASH_COMMANDS