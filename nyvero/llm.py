# How Python talks to an LLM
from openai import OpenAI

from .import config

client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL
)

def call_llm(messages, tools=None):
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=messages,
        tools=tools,
        reasoning_effort=config.REASONING_EFFORT,
        extra_body={
            "thinking": {
                "type": "enabled",
            }
        },
    )
    return response.choices[0].message

def stream_llm(messages, tools=None):
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=messages,
        tools=tools,
        reasoning_effort=config.REASONING_EFFORT,
        extra_body={
            "thinking": {
                "type": "enabled",
            }
        },
        stream=True,
    )

    return response

def collect_stream(response):
    content = ""
    reasoning_content = ""

    tool_calls = {}

    for chunk in response:
        delta = chunk.choices[0].delta

        reasoning = getattr(delta, "reasoning_content", None)

        if reasoning:
            reasoning_content += reasoning

        if delta.content:
            content += delta.content
            print(
                delta.content,
                end="",
                flush=True,
            )

        if delta.tool_calls:
            for tool_call in delta.tool_calls:
                index = tool_call.index

                if index not in tool_calls:
                    tool_calls[index] = {
                        "id": "",
                        "name": "",
                        "arguments": "",
                    }

                if tool_call.id:
                    tool_calls[index]["id"] += tool_call.id

                if tool_call.function:
                    if tool_call.function.name:
                        tool_calls[index]["name"] += (
                            tool_call.function.name
                        )

                    if tool_call.function.arguments:
                        tool_calls[index]["arguments"] += (
                            tool_call.function.arguments
                        )

    return {
        "content": content,
        "reasoning_content": reasoning_content,
        "tool_calls": list(tool_calls.values()),
    }

    # a dedicated summarizer

def summarize_messages(messages):
    prompt = {
        "role": "user",
        "content": (
            "Summarize this earlier coding-agent conversation.\n\n"
            "Preserve important facts such as:\n"
            "- files that were created or modified\n"
            "- user requirements\n"
            "- important technical decisions\n"
            "- errors and their resolutions\n"
            "- unfinished tasks\n\n"
            "Do not invent information.\n\n"
            f"Conversation:\n{messages}"
        ),
    }

    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[prompt],
        reasoning_effort=config.REASONING_EFFORT,
        extra_body={
            "thinking": {
                "type": "enabled",
            }
        },
    )

    return response.choices[0].message.content