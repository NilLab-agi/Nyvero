SAFE_TOOLS = {
    "read_file",
    "list_file",
    "file_exists"
}

CONFIRM_TOOLS = {
    "write_file",
    "edit_file",
    "delete_file",
    "bash"
}

def requires_confirmation(tool_name):
    return tool_name in CONFIRM_TOOLS