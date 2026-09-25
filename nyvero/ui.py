import json
from contextlib import contextmanager

from rich.align import Align
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text


ACCENT = "#7aa2f7"
USER = "#9ece6a"
TOOL = "#e0af68"
MUTED = "#565f89"

MAX_TOOL_OUTPUT_LINES = 12


class UI:
    def __init__(self):
        self.console = Console()

    
    # Main screen
    
    def banner(self):
        self.console.print()

        self._show_logo()

        self.console.print(
            Rule(
                Text(
                    " Nyvero ",
                    style=f"bold {ACCENT}",
                ),
                style=MUTED,
            )
        )

        self.console.print(
            Padding(
                Text(
                    "AI coding agent  ·  ctrl-d to exit",
                    style=MUTED,
                ),
                (0, 0, 0, 2),
            )
        )

    def _show_logo(self):
        logo = Text(
            "Nyvero",
            style=f"bold {ACCENT}",
        )

        self.console.print(
            Padding(
                Align.center(logo),
                (2, 0, 2, 0),
            )
        )

    def goodbye(self):
        self.console.print()

        self.console.print(
            Rule(
                Text(
                    " session ended ",
                    style=f"bold {MUTED}",
                ),
                style=MUTED,
            )
        )

    
    # Input

    def user(self, text):
        self.console.print(
            Padding(
                Text(
                    text.strip(),
                    style=f"bold {USER}",
                ),
                (1, 0, 0, 2),
            )
        )

    
    # Agent
    

    def agent(self, text):
        self.console.print(
            Padding(
                Group(
                    Text(
                        "nyvero",
                        style=f"bold {ACCENT}",
                    ),
                    Padding(
                        Markdown(text.strip()),
                        (1, 0, 0, 0),
                    ),
                ),
                (1, 2, 0, 2),
            )
        )

    
    # Tools
    

    def tool(self, name, args, result, nested=False):
        header = Text.assemble(
            (
                f"{name} ",
                f"bold {TOOL}",
            ),
            (
                self._format_args(args),
                MUTED,
            ),
        )

        self.console.print(
            Padding(
                Panel(
                    Group(
                        header,
                        Rule(style=MUTED),
                        self._format_result(result),
                    ),
                    border_style=MUTED,
                    padding=(0, 1),
                ),
                (1, 2, 0, 6 if nested else 2),
            )
        )

    def tool_call(self, name, args):
        self.console.print(
            Padding(
                Text.assemble(
                    (f"→ {name}", f"bold {TOOL}"),
                    ("  " + self._format_args(args), MUTED),
                ),
                (1, 2, 0, 2),
            )
        )

    
    # Errors


    def error(self, message):
        self.console.print(
            Padding(
                Panel(
                    Text(
                        message,
                        style=TOOL,
                    ),
                    title=Text(
                        "error",
                        style=f"bold {TOOL}",
                    ),
                    title_align="left",
                    border_style=TOOL,
                    padding=(0, 1),
                ),
                (1, 2, 0, 2),
            )
        )


    # Working

    @contextmanager
    def working(self, label="thinking"):
        with self.console.status(
            Text(
                label,
                style=MUTED,
            ),
            spinner="dots",
            spinner_style=ACCENT,
        ):
            yield


    # Context

    def context_status(self, count):
        self.console.print(
            Padding(
                Text(
                    f"context · {count} messages",
                    style=MUTED,
                ),
                (0, 0, 0, 2),
            )
        )

    # Permission

    def confirm(self, name, args):
        self.console.print(
            Padding(
                Text(
                    f"Allow {name}? {self._format_args(args)}",
                    style=f"bold {TOOL}",
                ),
                (1, 0, 0, 1),
            )
        )

        try:
            answer = input("  allow? (y/n)> ").strip()
        except (EOFError, KeyboardInterrupt):
            return False

        return answer.lower().startswith("y")

    # Todos

    def todos(self, todos):
        rows = Table.grid(padding=(0, 1))

        rows.add_column(no_wrap=True)
        rows.add_column(overflow="fold")

        for todo in todos:
            status = todo["status"]

            if status == "completed":
                mark = "✓"
                style = f"strike {MUTED}"

            elif status == "in_progress":
                mark = "→"
                style = f"bold {ACCENT}"

            else:
                mark = "○"
                style = MUTED

            rows.add_row(
                Text(mark, style=style),
                Text(todo["content"], style=style),
            )

        completed = sum(
            1
            for todo in todos
            if todo["status"] == "completed"
        )

        self.console.print(
            Padding(
                Panel(
                    rows,
                    title=Text(
                        f"todos {completed}/{len(todos)}",
                        style=f"bold {TOOL}",
                    ),
                    title_align="left",
                    border_style=MUTED,
                    padding=(0, 1),
                ),
                (1, 2, 0, 2),
            )
        )

    # Subagent

    def subagent(self, description):
        self.console.print(
            Padding(
                Panel(
                    Text(
                        description.strip(),
                        style=MUTED,
                    ),
                    title=Text(
                        "subagent · own context",
                        style=f"bold {ACCENT}",
                    ),
                    title_align="left",
                    border_style=ACCENT,
                    padding=(0, 1),
                ),
                (1, 2, 0, 4),
            )
        )

    # Context compaction

    def compacted(self, before, after):
        self.console.print(
            Padding(
                Panel(
                    Text(
                        f"context compacted: "
                        f"{before} → {after} messages",
                        style=MUTED,
                    ),
                    title=Text(
                        "compacted",
                        style=f"bold {TOOL}",
                    ),
                    title_align="left",
                    border_style=TOOL,
                    padding=(0, 1),
                ),
                (1, 2, 0, 2),
            )
        )

    # Helpers

    def _format_args(self, args):
        if not args:
            return ""

        if len(args) == 1:
            return str(next(iter(args.values())))

        return json.dumps(
            args,
            ensure_ascii=False,
        )

    def _format_result(self, result):
        if result is None:
            return Text(
                "(no output)",
                style=MUTED,
            )

        lines = str(result).strip().splitlines()

        if not lines:
            lines = ["(no output)"]

        shown = lines[:MAX_TOOL_OUTPUT_LINES]

        body = Text(
            "\n".join(shown),
            style=MUTED,
        )

        hidden = len(lines) - len(shown)

        if hidden:
            body.append(
                f"\n… {hidden} more lines",
                style=f"italic {TOOL}",
            )

        return body


ui = UI()