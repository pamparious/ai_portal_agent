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
        print("Starting Playwright...")
        playwright_instance = await async_playwright().start()
        
        print("Connecting to browser...")
        await agent.connect_to_browser(playwright_instance)
        
        print("Testing portal status...")
        try:
            status = await agent.check_portal_status()
            print("Portal status:")
            pprint(status)
        except Exception as e:
            print(f"Error checking portal status: {e}")
        
        print("\nTesting available models...")
        try:
            models = await agent.list_available_models()
            print("Available models:")
            pprint(models)
        except Exception as e:
            print(f"Error listing models: {e}")
        
        print("\nSending 'ask_ai' tool call...")
        try:
            query = "What is the capital of France?"
            response_text = await agent.ask_ai(query)
            print("Received response:")
            pprint({"response": response_text})
        except Exception as e:
            print(f"Error calling ask_ai tool: {e}")
            traceback.print_exc()
            
        print("\nTesting session info...")
        try:
            session = await agent.get_portal_session()
            print("Session info:")
            pprint(session)
        except Exception as e:
            print(f"Error getting session info: {e}")
            
    except Exception as e:
        print(f"Error running test client: {e}")
        traceback.print_exc()
    finally:
        print("\nCleaning up...")
        if agent:
            await agent.close()
        if playwright_instance:
            await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(main())