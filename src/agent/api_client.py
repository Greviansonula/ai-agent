from tenacity import retry, stop_after_attempt, wait_exponential
import anthropic
from ..utils.config import load_config


class AnthropicAPIClient:
    def __init__(self):
        config = load_config()
        self.client = anthropic.AsyncAnthropic()
        self.model = config["model"]["name"]
        self.max_tokens = config["model"]["max_tokens"]


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def generate_response(self, messages, tools):
        """Generate response with context management."""
        return await self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            max_tokens=self.max_tokens,
            messages=messages,
            tools=tools,
        )