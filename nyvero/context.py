from .prompt import SYSTEM_PROMPT

MAX_CONTEXT_CHARS = 20_000
RECENT_MESSAGE_COUNT = 10
class Context:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

    def add_user_message(self, content):
        self.messages.append({
            "role": "user",
            "content": content,
        })

    def add_assistant_message(self, message):
        self.messages.append(message)

    def add_tool_result(self, tool_call_id, content):
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content,
        })

    def get_messages(self):
        return self.messages

    def message_count(self):
        return len(self.messages)
    
    def estimated_size(self):
        return sum(
            len(message.get("content", ""))
            for message in self.messages
            if isinstance(message.get("content"), str)
        )
    
    def needs_compaction(self):
        return self.estimated_size() > MAX_CONTEXT_CHARS

    # A way to inspect oldmessages

    def get_old_messages(self):
        return self.messages[1:-RECENT_MESSAGE_COUNT]
    
    def get_recent_messages(self):
        return self.messages[-RECENT_MESSAGE_COUNT:]

    # Don't let Context call LLM

    def replace_old_messages(self, summary):
        recent_messages = self.get_recent_messages()

        self.messages = [
            self.messages[0],
            {
                "role": "system",
                "content": f"Previos conversation summary: \n{summary}"
            },
            *recent_messages,
        ]