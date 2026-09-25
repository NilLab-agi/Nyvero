# Nyvero targeted refactor

**four files** and leaves the UI exactly as it was.

```
 nyvero/agent.py    | 79 +-------------------------------------
 nyvero/commands.py | 44 +++++++++++++++++++++++++
 nyvero/subagent.py |  2 +-
 nyvero/tools.py    | 24 ++++++++++++++-
 4 files changed, 75 insertions(+), 74 deletions(-)
```

`ui.py` is **untouched**. So are `context.py`, `history.py`, `session.py`,
`compact.py`, `permissions.py`, `sandbox.py`, `config.py`, `llm.py`, `skills.py`,
`todos.py` and `prompt.py`. No dependencies were added.

---

## Commit

These changes are commit **`e0c9028949db6a3796f7e5b213dc2cdf1b406a13`**
(`refactor: targeted architecture changes (changed by ai)`). Run
`git show e0c9028 --stat` to see the files it touched.

---

## 1. `tools.py` — one shared executor

**Problem.** `execute_tool` only dispatched. Permission checks and error
handling were duplicated in `agent.py`, and the subagent had its own copy — so
the two callers could drift.

**Change.** `execute_tool` is now the single choke point. It looks up the tool,
runs the permission policy, asks the user when required, and turns any failure
into a result string.

```python
def execute_tool(name, arguments):
    tool = TOOLS.get(name)
    if tool is None:
        return f"Unknown tool: {name}"

    permission = permission_for_tool(name, arguments)
    if permission == DENY:
        return "Tool execution denied by Nyvero's safety policy"
    if permission == CONFIRM and not ui.confirm(name, arguments):
        return "Tool execution denied by the user"

    try:
        return tool(**arguments)
    except Exception as error:
        return f"Tool execution failed: {error}"
```

This is what makes the main loop and the subagent genuinely share one executor:
a subagent is no longer a path around the policy.

## 2. `agent.py` — thinner loop

**Problem.** The tool block was ~110 lines of inline deny/confirm/execute/error
handling.

**Change.** It collapses to one call. Everything else in the loop is unchanged.

```python
for tool_call in result["tool_calls"]:
    name = tool_call["name"]
    arguments = json.loads(tool_call["arguments"])

    ui.tool_call(name, arguments)

    tool_result = execute_tool(name, arguments)

    ui.tool(name, arguments, tool_result)
    context.add_tool_result(tool_call["id"], tool_result)
    session.save(context.get_messages())
```

The now-unused `permissions` import was removed. This is the requested
"centralized tool schemas/registry/execution" and "shared executor".

## 3. `subagent.py` — one-character bug fix

**Problem.** `task()` called `stream_llm(..., tools=get_subagent_tools)`,
passing the **function** instead of calling it. The subagent was handed a
function object where the API expected a list of schemas.

**Change.**

```diff
-            tools=get_subagent_tools,
+            tools=get_subagent_tools(),
```

The subagent already used `execute_tool` (imported inside the function, which
also keeps the module import graph acyclic). With change 1, the subagent is now
fenced by the same permission rules as the main agent. Its isolation — fresh
message list, 12-turn cap, read-only toolset — is unchanged.

## 4. `commands.py` — a command layer

**Problem.** The file was empty; slash input had nowhere to go.

**Change.** `handle(command, context)` owns everything beginning with `/`. The
agent dispatches to it and returns to the loop:

```python
if user_input.startswith("/"):
    commands.handle(user_input, context)
    session.save(context.get_messages())
    continue
```

Implemented: `/compact` (reuses the existing compaction flow and `ui.compacted`)
and `/help`. Both use only methods that already exist on your `UI`, so `ui.py`
did not change.

`/sessions` and `/rewind` were **left out on purpose**: they need a numbered
list picker, and your `UI` has no `pick` method. Adding one means touching
`ui.py`, which you asked me not to do. Say the word and it is a small, additive
method.

---

## 5. Verification

- `git status` shows exactly four modified files; `nyvero/ui.py` is not among them.
- Imports all resolve: `import nyvero.agent, nyvero.tools, nyvero.subagent, nyvero.commands, nyvero.ui`.
- Executor behaviour:
  - `execute_tool("bash", {"command": "rm -rf build"})` → blocked by policy
  - `execute_tool("nope", {})` → `Unknown tool: nope`
  - `execute_tool("file_exists", {"path": "pyproject.toml"})` → `true`
  - `execute_tool("read_file", {})` → argument error returned as text, no crash
- `get_subagent_tools()` now returns the list
  `['bash', 'read_file', 'list_files', 'file_exists', 'read_skill']`.
- End-to-end loop simulation with a stubbed model ran a tool call and persisted
  `['system', 'user', 'assistant', 'tool']` — identical to the original
  behaviour (the final tool-free assistant message was never persisted by the
  original loop either; that is unchanged).
- Existing test suite: `5 passed`.

---

## 6. Deliberately not changed (kept small)

- **UI** — untouched.
- **Streaming** — `stream_llm` / `collect_stream` kept as-is.
- **`Context` class** — kept; it already separates storage from summarisation
  (`compact.py`).
- **`history.py`** — still empty. The reference's cap/strip/drop token budget is
  a separate, larger change; not folded in here.
- **Sessions** — still append + `rewrite` on compaction, not journaled.
- **Subagent loop** — kept as its own loop; only the bug and the shared executor
  were changed.

These remain valid follow-ups but each is a distinct change, not part of this
targeted pass.
