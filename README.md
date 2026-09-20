# Nyvero

A minimal AI coding-agent harness built from scratch — one loop, one LLM, a handful of tools.

## What it is

Nyvero is a lightweight coding agent that connects an LLM to tools such as filesystem
operations and shell commands. You give it a task; it decides which tools to call, runs
them, feeds the results back to the model, and repeats until it has an answer.

There is no agent framework underneath. The loop, the tool definitions, and the tool
execution are written in plain Python, so every step stays readable and inspectable.

## Why it exists

Agent frameworks hide the interesting parts behind abstractions. Nyvero exists to take
those parts apart and rebuild them by hand: how a tool call round-trip actually works,
how conversation state is tracked, when and how to truncate it, and where the safety
boundaries belong.

It is a learning project first. The goal is understanding, not feature parity.

## Architecture

```text
User
 ↓
Nyvero CLI
 ↓
Agent
 ↓
LLM (OpenRouter)
 ↓
Tool calls
 ↓
Tool execution
 ↓
Tool results
 ↓
LLM
```

The agent loop sits between the CLI and the model. It sends the conversation to the LLM,
inspects the response for tool calls, executes them, appends the results as messages, and
loops again until the model responds without requesting a tool.

## Tech stack

* Python 3.12+
* [uv](https://docs.astral.sh/uv/) for environments and dependency management
* OpenRouter as the model provider (OpenAI-compatible API)
* [OpenRouter Python SDK](https://openrouter.ai/docs/sdks/python) as the model client
* python-dotenv for loading credentials from `.env`

## Current status

Early, and intentionally so. What is in place today:

* Package layout (`nyvero/`) with a working CLI entry point
* A `nyvero` console script that runs and prints a banner
* An LLM client (`llm.py`) that reaches OpenRouter through the OpenRouter Python SDK

What is not built yet: the agent loop, tool calling, and every tool. `agent.py` and the
remaining modules are empty placeholders, so Nyvero can talk to a model but cannot yet
call a tool or act on its own.

## Roadmap

Built incrementally, one concept at a time:

1. LLM client (OpenRouter via the OpenAI SDK)
2. Agent loop
3. Tool calling
4. Filesystem and shell tools
5. Context and history
6. Permissions
7. Sandboxing
8. Compaction
9. Sessions
10. Skills
11. Subagents
12. Todos
13. Git integration
14. Production hardening

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). If you do not have uv
installed yet, install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then clone the repository and install the dependencies:

```bash
git clone https://github.com/NilLab-agi/Nyvero.git
cd Nyvero
uv sync
```

## Run

```bash
uv run nyvero
```

Expected output for now:

```text
Nyvero
```

### Configuration

Copy `.env.example` to `.env` and add your OpenRouter key:

```bash
cp .env.example .env
```

```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
MODEL=liquid/lfm-2.5-2.6b:free
```

`config.py` loads `.env` from the repository root and fails fast when the key is missing
or does not look like an OpenRouter key. A key exported in your shell overrides the file,
so keep the real key in `.env` only.

## Note

Nyvero is written from scratch for learning, after studying how minimal coding-agent
architectures are put together. Ideas and patterns are borrowed from that study; the
implementation here is its own.

## License

MIT — see [LICENSE](LICENSE).
