from dataclasses import dataclass, field
from typing import Any, List
from anthropic.types import Message, ToolUnionParam
from .api_client import AnthropicAPIClient
from .memory_manager import MemoryManager
from .tool_handler import ToolHandler
from ..interface.cli import CLIInterface
from ..utils.config import load_config