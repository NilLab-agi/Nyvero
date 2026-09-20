# The actual agent loop
from .llm import call_llm


def main():
    user_input = input("You: ")

    messages = [
        {
            "role": "user",
            "content": user_input,
        }
    ]

    message = call_llm(messages)

    print(f"\nNyvero: {message.content}")


if __name__ == "__main__":
    main()