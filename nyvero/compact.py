from .llm import summarize_messages

RECENT_MESSAGE_COUNT = 10

COMPACTION_PROMPT = """
You are compacting the history of a coding agent session.

Your job is to create a handoff summary that allows a future coding
agent to continue the work without reading the messages that are being
removed from the context.

Preserve important information, not conversational filler.

Use these sections:

## Goal
Describe what the user is trying to accomplish.
Preserve exact wording when the user's requirement matters.

## What happened
Describe important decisions, approaches that were tried, errors
encountered, and approaches that were rejected.
Do not remove information that would prevent the future agent from
repeating a failed approach.

## Files
List every file that was created, modified, deleted, or discussed
in a way that materially affects the current work.
Include the path and what changed.

## State
Describe what currently works, what is broken, and what remains
unfinished.

## Next
Describe the immediate next step the future agent should take.

Rules:

- Be specific.
- Preserve file paths, function names, commands, and important errors.
- Preserve explicit user requirements and corrections.
- Preserve decisions and rejected approaches when they matter.
- Do not invent progress or facts that are not present in the transcript.
- Do not claim something works unless the transcript shows that it works.
- Prefer actionable information over conversational details.
- Keep the summary substantially shorter than the original transcript.
- Do not include a preamble or sign-off.
- Start directly with the first section.
"""

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

    summary = summarize_messages(
        old_messages,
        COMPACTION_PROMPT,
        )

    # return [
    #     messages[0],
    #     {
    #         "role": "sytem",
    #         "content": (
    #             "Previous conversation summary: \n\n"
    #             + summary
    #         ),
    #     },
    #     *recent_messages,
    # ]

    return summary


    