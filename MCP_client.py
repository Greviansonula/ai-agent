#!/usr/bin/env python3
import asyncio
from src.agent.core import SupportAgent
from src.interface.cli import CLIInterface
from mcp.client.stdio import std_client
from mcp import ClientSession, StdioServerParameters


server_params = StdioServerParameters(
    command="python",  # Executable
    args=["./MCP_server.py"],  # Optional command line arguments
    env=None,  # Optional environment variables
)


async def main():
    async with std_client(server_params) as (read, write):
        print("✅ Connection established")
        async with ClientSession(read, write) as session:
            # Initialize the support agent
            print("🔄 Initializing session...")
            agent = SupportAgent()
            await session.initialize()
            print("✅ Session initialized")
            await CLIInterface(agent).start_chat_loop()

if __name__ == "__main__":
    asyncio.run(main())