from anthropic import AsyncAnthropic
from ..utils.config import load_config

class MemoryManager:
    """Conversation history and context window management."""

    def __init__(self):
        config = load_config()
        self.client = AsyncAnthropic()
        self.max_context = config["model"]["context_window "]

    async def truncate_history(self, messages) -> None:
        """Truncate conversation history to fit within the context window: token limits"""
        while await self._current_tokens(messages) > self.max_context:
            if len(messages) == 1:
                messages.pop(1)
            else:
                break
    
    async def _current_tokens(self, messages) -> int:
        """Calculate the number of tokens in the current conversation history."""
        return await self.client.count_tokens(
            messages=messages
            ).input_tokens