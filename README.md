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
* OpenAI Python SDK as the OpenRouter-compatible client
* python-dotenv for loading credentials from `.env`

## Current status

Early, and intentionally so. What is in place today:

* Package layout (`nyvero/`) with a working CLI entry point
* A `nyvero` console script that runs and prints a banner

What is not built yet: the LLM client, the agent loop, tool calling, and every tool.
`agent.py` and `llm.py` are empty placeholders, and no third-party dependencies are
declared in `pyproject.toml` yet. Nyvero does not talk to a model at this stage.

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

Once the LLM client lands, an OpenRouter API key will be read from the environment:

```bash
# .env
OPENROUTER_API_KEY=your-key-here
```

This is not wired up yet — Nyvero does not make any API calls in its current state.

## Note

Nyvero is written from scratch for learning, after studying how minimal coding-agent
architectures are put together. Ideas and patterns are borrowed from that study; the
implementation here is its own.

## License

MIT — see [LICENSE](LICENSE).
