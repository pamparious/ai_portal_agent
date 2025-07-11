import asyncio
import sys
import traceback
from pprint import pprint
from datetime import timedelta
import os
from playwright.async_api import async_playwright

from mcp_server.browser_agent import BrowserAgent
from src.portal.portal_interface import PortalInterface

async def main() -> None:
    """Test client for MCP server. Sends an 'ask_ai' tool call and prints the response."""
    agent = BrowserAgent()
    playwright_instance = None
    try:
        playwright_instance = await async_playwright().start()
        await agent.connect_to_browser(playwright_instance)
        
        print("Sending 'ask_ai' tool call...")
        try:
            query = "What is the capital of France?"
            response_text = await agent.ask_ai(query)
            print("Received response:")
            pprint({"response": response_text})
        except Exception as e:
            print(f"Error calling tool: {e}")
            traceback.print_exc()
    except Exception as e:
        print(f"Error running test client: {e}")
        traceback.print_exc()
    finally:
        if agent:
            await agent.close()
        if playwright_instance:
            await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(main())