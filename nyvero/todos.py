todos = []

def add_todo(content: str) -> dict:
    todo = {
        "id": len(todos) + 1,
        "content": content,
        "status": "pending",
    }

    todos.append(todo)
    return todo

def list_todos() -> list[dict]:
    return todos

def update_todo(todo_id: int, status: str) -> dict | str:
    for todo in todos:
        if todo["id"] == todo_id:
            todo["Status"] = status
            return todo
    
    return f"Todo not found: {todo_id}"

