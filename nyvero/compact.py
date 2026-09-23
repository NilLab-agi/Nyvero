from .llm import summarize_messages

RECENT_MESSAGE_COUNT = 10

def find_cutoff(messages):
    """ find where the old conversation ends and the recent conversation begins.
    """
    if len(messages) <= RECENT_MESSAGE_COUNT + 1:
      return 1

    return len(messages) - RECENT_MESSAGE_COUNT

def compact(messages):
    """
    Summaeize old messages and keep recent message unchanged
    """
    cutoff = find_cutoff(messages)

    if cutoff <= 1:
        return messages

    old_messages = messages[1:cutoff]
    recent_messages = messages[cutoff:]

    summary = summarize_messages(old_messages)

    return [
        messages[0],
        {
            "role": "sytem",
            "content": (
                "Previous conversation summary: \n\n"
                + summary
            ),
        },
        *recent_messages,
    ]
    