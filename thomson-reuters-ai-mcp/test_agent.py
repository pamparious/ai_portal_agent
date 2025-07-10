import asyncio
import sys
import traceback
from pprint import pprint
from datetime import timedelta
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


async def main() -> None:
    """Test client for MCP server. Sends an 'ask_ai' tool call and prints the response."""
    # Use the current Python executable for portability
    python_executable = sys.executable
    server_parameters = StdioServerParameters(
        command=python_executable,
        args=["-m", "mcp.server"],
    )
    try:
        async with stdio_client(server_parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("Sending 'ask_ai' tool call...")
                try:
                    response = await session.call_tool("ask_ai", {"query": "What is the capital of France?"}, read_timeout_seconds=timedelta(seconds=30))
                    print("Received response:")
                    pprint(response)
                except Exception as e:
                    print(f"Error calling tool: {e}")
                    traceback.print_exc()
    except Exception as e:
        print(f"Error running test client: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())