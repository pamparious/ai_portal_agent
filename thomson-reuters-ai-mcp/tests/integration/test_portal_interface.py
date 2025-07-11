import pytest
import asyncio
from playwright.async_api import async_playwright
from mcp_server.browser_agent import BrowserAgent
from src.portal.portal_interface import PortalInterface
from pytest_asyncio import fixture as async_fixture

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
async def test_portal_interface_functionality(browser_agent_instance):
    """
    Tests the basic functionality of the PortalInterface.
    This test assumes a browser is connected and navigated to the AI portal.
    """
    portal_interface = PortalInterface(browser_agent_instance.page)

    # Test detect_chat_interface
    chat_detected = await portal_interface.detect_chat_interface()
    assert chat_detected is True, "Chat interface should be detected"

    # Test send_message and wait_for_response
    test_query = "Hello, AI!"
    await portal_interface.send_message(test_query)
    response = await portal_interface.wait_for_response()
    assert "response" in response.lower(), "AI should provide a response"

    # Test take_screenshot
    screenshot_path = "test_portal_screenshot.png"
    await portal_interface.take_screenshot(screenshot_path)
    # You might want to add a check here to ensure the file exists
    # For now, just ensure no exception is raised
    import os
    assert os.path.exists(screenshot_path)

    print(f"Test query: {test_query}")
    print(f"AI response: {response}")
    print(f"Screenshot saved to: {screenshot_path}")
