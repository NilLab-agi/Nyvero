<p align="center">
  <img src="https://raw.githubusercontent.com/NilLab-agi/Nyvero/main/additional/Nyvero.png" alt="Nyvero" width="440">
</p>

<p align="center">
  A minimal AI coding agent harness, written from scratch in Python.<br>
  One loop. One model. A handful of tools. No framework.
</p>

<p align="center">
  Built by <a href="https://github.com/nilaymallikk">Nilay Mallik</a> · https://github.com/nilaymallikk
</p>

---

Nyvero is a lightweight coding agent you can read end to end. Give it a task and
it decides which tools to call, runs them, feeds the results back to the model,
and repeats until it has an answer. The loop, the tools, the permission rules
and the sandbox are all plain Python — no hidden layers.

It is a **learning project first**: the goal is understanding how a coding agent
works, not matching production assistants feature for feature.

## Demo

▶ [Watch the Nyvero demo](https://raw.githubusercontent.com/NilLab-agi/Nyvero/main/additional/nyvero_demo.mp4)

## Architecture

<p align="center">
  <img src="https://raw.githubusercontent.com/NilLab-agi/Nyvero/main/additional/architecture.png" alt="Nyvero architecture" width="620">
</p>

The loop sends the conversation to the model, inspects the response for tool
calls, runs each one through the **same** permission-checked executor, appends
the results, and repeats until the model answers without a tool. Subagents run
that same loop against a fresh, read-only context and return only a final
report.

```
nyvero/
├── agent.py        # the loop: user ↔ model ↔ tools
├── commands.py     # slash commands (/compact, /help)
├── llm.py          # provider client and streaming
├── tools.py        # tool schemas, registry, shared executor
├── permissions.py  # allow / confirm / deny policy
├── sandbox.py      # OS sandbox for bash (seatbelt / bubblewrap)
├── subagent.py     # isolated, read-only exploration agent
├── context.py      # message history and compaction trigger
├── compact.py      # summarisation prompt and handoff note
├── session.py      # JSONL session persistence
├── skills.py       # skill discovery and loading
├── todos.py        # todo list state
├── prompt.py       # system prompt
├── config.py       # environment configuration
└── ui.py           # terminal presentation
```

## Features

- **Thin agent loop** — the whole round trip is a few dozen readable lines.
- **Streamed responses** in a rich terminal UI.
- **One shared tool executor** used by the main agent and its subagents.
- **Filesystem + shell tools** with permission tiers and workspace confinement.
- **Sandboxed shell** — read-only root, writable workspace, no network. Uses
  bubblewrap on Linux and the built-in seatbelt on macOS.
- **Skills, todos and subagents** — reusable instructions, multi-step planning,
  and isolated read-only exploration.

## Install

Requires **Python 3.12+** and [uv](https://docs.astral.sh/uv/).

### Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo apt install bubblewrap      # Fedora: sudo dnf install bubblewrap

git clone https://github.com/NilLab-agi/Nyvero.git
cd Nyvero
uv sync
```

Shell commands run inside [bubblewrap](https://github.com/containers/bubblewrap).

### macOS

```bash
brew install uv                  # or: curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/NilLab-agi/Nyvero.git
cd Nyvero
uv sync
```

Shell commands run inside the built-in `sandbox-exec` (seatbelt) — nothing extra
to install.

### Windows

Use **WSL2** and follow the Linux steps — that is the only way to get a
sandboxed shell. Native Windows runs Nyvero too, but the shell is not
kernel-confined (the permission rules still apply).

```powershell
wsl --install                    # then, inside Ubuntu:
# curl -LsSf https://astral.sh/uv/install.sh | sh
# sudo apt install bubblewrap
# git clone https://github.com/NilLab-agi/Nyvero.git && cd Nyvero && uv sync
```

### Run

```bash
cp .env.example .env      # then add your API key
uv run nyvero
```

`config.py` loads `.env` with [python-dotenv](https://github.com/theskumar/python-dotenv):

| Variable | Default | Description |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | — | **Required.** Key for the model provider. |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | Any OpenAI-compatible endpoint. |
| `MODEL` | `deepseek-flash` | Model identifier. |
| `REASONING_EFFORT` | `high` | Reasoning-effort hint. |

## Usage

```bash
uv run nyvero            # new session
uv run nyvero --resume   # continue the most recent session
```

Type `exit`, `quit`, or press <kbd>Ctrl</kbd>+<kbd>D</kbd> to leave.

| Slash command | Description |
| --- | --- |
| `/compact` | Summarise history and free up the context window. |
| `/help` | List commands. |

## Tools

Nyvero is model- and provider-agnostic: **any OpenAI-compatible provider and any
model work** — OpenRouter, OpenAI, DeepSeek, Groq, Together, a local
Ollama/vLLM server, and so on. Point `DEEPSEEK_BASE_URL` at the provider and set
`MODEL` to the model you want; nothing in the loop or the tools is tied to a
specific vendor.

| Tool | Description | Permission |
| --- | --- | --- |
| `bash` | Run a shell command (sandboxed). | allow / confirm / deny |
| `read_file` · `list_files` · `file_exists` | Inspect the workspace. | allow |
| `write_file` · `edit_file` · `delete_file` | Change files. | confirm |
| `read_skill` | Load a skill's instructions. | allow |
| `add_todo` · `list_todos` · `update_todo` | Track multi-step work. | allow |
| `task` | Delegate read-only exploration to a subagent. | allow |

## Safety

- **Sandboxed shell** — read-only root, writable workspace, no network.
  bubblewrap on Linux, seatbelt on macOS. Where neither exists (native
  Windows) commands still run, gated by permissions; only the kernel layer is
  missing.
- **Permissions** — reads run freely; writes and non-trivial shell commands ask;
  destructive commands (`rm`, `sudo`, `curl`, `git push`, …) are denied.
- **Workspace confinement** — file tools refuse paths outside the project.

## Development

```bash
uv sync
uv run pytest
```

## License

Released under the [MIT License](LICENSE). Nyvero is written for learning,
after studying [`avbiswas/neural-code`](https://github.com/avbiswas/neural-code).
