from nyvero.llm import LLM


def main():
    llm = LLM()

    response = llm.chat(
        [
            {
                "role": "user",
                "content": "Say hello to Nyvero in one sentence.",
            }
        ]
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()