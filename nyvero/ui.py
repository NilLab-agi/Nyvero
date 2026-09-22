def show_header() -> None:
    print()
    print("╭──────────────────────────────╮")
    print("│           Nyvero             │")
    print("│      AI Coding Agent         │")
    print("╰──────────────────────────────╯")


def get_input() -> str:
    return input("\nYou: ").strip()


def show_message(message: str) -> None:
    print(f"\nNyvero: {message}")


def show_tool_call(name: str, arguments: dict) -> None:
    print(f"\n🔧 {name}")

    for key, value in arguments.items():
        print(f"   {key}: {value}")


def show_tool_result(result: str) -> None:
    print("\n   ↳ Tool result:")

    if result:
        print(result)
    else:
        print("(no output)")


def show_error(message: str) -> None:
    print(f"\n❌ Error: {message}")


def show_goodbye() -> None:
    print("\nGoodbye!")