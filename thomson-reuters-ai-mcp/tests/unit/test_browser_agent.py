import pytest
import asyncio
import sys
import os
from playwright.async_api import async_playwright
from pytest_asyncio import fixture as async_fixture

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server.browser_agent import BrowserAgent
from src.portal.portal_interface import PortalInterface

@async_fixture(scope="function")
async def browser_agent_instance():
    """Fixture to provide a connected BrowserAgent instance."""
    agent = BrowserAgent()
    playwright_instance = await async_playwright().start()
    try:
        await agent.connect_to_browser(playwright_instance)
        yield agent
    finally:
        await agent.close()
        await playwright_instance.stop()

@pytest.mark.asyncio
async def test_login_and_chat_interface(browser_agent_instance):
    """
    Tests the login status and chat interface detection.
    """
    portal_interface = PortalInterface(browser_agent_instance.page)

    # Check if the chat interface is detected (implies successful navigation and potentially login)
    chat_detected = await portal_interface.detect_chat_interface()
    assert chat_detected is True, "Chat interface should be detected after navigation and login."

    print(f"Chat interface detected: {chat_detected}")