# How Python talks to an LLM
from openai import OpenAI

from .import config

client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL
)

def call_llm(messages):
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=messages,
        reasoning_effort=config.REASONING_EFFORT,
        extra_body={
            "thinking": {
                "type": "enabled",
            }
        },
    )
    return response.choices[0].message