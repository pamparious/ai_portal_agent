import asyncio
import logging
import time
import subprocess
import sys
from typing import Dict, List, Optional, Any
from playwright.async_api import Browser, Page, expect, async_playwright
from src.portal.portal_interface import PortalInterface
from .exceptions import BrowserConnectionError, PortalError, AuthenticationError, OperationTimeoutError
from .config import get_config

logger = logging.getLogger(__name__)

class BrowserAgent:
    """Manages browser connection and interaction with the AI portal."""
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.portal_interface: Optional[PortalInterface] = None
        self.playwright_instance = None
        self.config = get_config()
        self.connection_health_check_interval = 30  # seconds
        self.last_health_check = 0

    async def _check_browser_debug_port(self) -> bool:
        """Check if browser debug port is accessible"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', self.config.browser.debug_port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug("Debug port check failed: %s", e)
            return False

    async def _get_browser_info(self) -> Optional[Dict[str, Any]]:
        """Get browser information from debug endpoint"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{self.config.browser.debug_port}/json/version", timeout=2) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
        except Exception as e:
            logger.debug("Failed to get browser info: %s", e)
        return None

    async def connect_to_browser(self, playwright_instance, max_retries: int = 3):
        """Connect to existing browser (Edge or Chrome) with retry logic"""
        logger.info("Connecting to existing browser session...")

        # First check if debug port is accessible
        if not await self._check_browser_debug_port():
            logger.warning("Debug port %d is not accessible", self.config.browser.debug_port)
            logger.info("Checking for browser processes and debug port availability...")

        # Get browser info if available
        browser_info = await self._get_browser_info()
        if browser_info:
            logger.info("Found browser: %s - WebKit: %s",
                         browser_info.get('Browser', 'Unknown'),
                         browser_info.get('WebKit-Version', 'Unknown'))

        for attempt in range(max_retries):
            try:
                # Connect to an existing browser instance via CDP
                endpoint_url = f"http://localhost:{self.config.browser.debug_port}"
                logger.info("Attempting to connect to browser at %s (attempt %d)",
                             endpoint_url, attempt + 1)

                self.browser = await playwright_instance.chromium.connect_over_cdp(
                    endpoint_url,
                    timeout=self.config.browser.timeout
                )

                # Get the first page or create new one
                if self.browser.contexts and self.browser.contexts[0].pages:
                    self.page = self.browser.contexts[0].pages[0]
                else:
                    context = await self.browser.new_context()
                    self.page = await context.new_page()

                self.portal_interface = PortalInterface(self.page)
                logger.info("Connected to browser. Current URL: %s", self.page.url)

                # Navigate to the AI portal if not already there
                portal_url = self.config.get_portal_url()
                expected_url_part = "dataandanalytics.int.thomsonreuters.com/ai-platform"

                if expected_url_part not in self.page.url:
                    logger.info("Navigating to AI portal: %s", portal_url)
                    await self.page.goto(portal_url, timeout=self.config.browser.timeout)
                    await self.page.wait_for_load_state("networkidle")
                    logger.info("Navigated to %s", self.page.url)

                # Update health check timestamp
                self.last_health_check = time.time()
                logger.info("Browser connection established successfully")
                return

            except Exception as e:
                logger.warning("Connection attempt %d failed: %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * self.config.portal.retry_delay
                    logger.info("Retrying in %d seconds...", wait_time)
                    await asyncio.sleep(wait_time)
                else:
                    logger.error("Failed to connect to browser after %d attempts", max_retries)
                    raise BrowserConnectionError(f"Failed to connect to browser: {e}") from e

    async def ask_ai(self, query: str) -> str:
        """Send query to AI portal and return response"""
        if not self.page:
            raise RuntimeError("Browser not connected. Call connect_to_browser first.")

        # Validate input
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if len(query) > self.config.security.max_query_length:
            raise ValueError(f"Query too long. Maximum length: {self.config.security.max_query_length}")

        # Check connection health
        await self._check_connection_health()

        logger.info("Asking AI: %s...", query[:100] if len(query) > 100 else query)

        try:
            await self.portal_interface.send_message(query)
            response_text = await self.portal_interface.wait_for_response(timeout=self.config.portal.response_timeout)

            # Validate response length
            if len(response_text) > self.config.security.max_response_length:
                logger.warning("Response truncated. Original length: %d", len(response_text))
                response_text = response_text[:self.config.security.max_response_length] + "...[truncated]"

            logger.info("Received AI response: %s...", response_text[:100] if len(response_text) > 100 else response_text)
            return response_text

        except Exception as e:
            logger.error("Error during AI interaction: %s", e)
            raise PortalError(f"Failed to get AI response: {e}") from e

    async def check_portal_status(self) -> Dict[str, Any]:
        """Check portal status and connection health"""
        if not self.page:
            return {
                "browser_connected": False,
                "authenticated": False,
                "available_models": [],
                "session_status": "disconnected"
            }

        try:
            # Check browser connection
            await self._check_connection_health()

            # Check authentication status
            authenticated = await self._check_authentication()

            # Get available models
            available_models = await self.list_available_models()

            return {
                "browser_connected": True,
                "authenticated": authenticated,
                "available_models": available_models,
                "session_status": "active",
                "portal_url": self.page.url,
                "last_health_check": self.last_health_check
            }

        except Exception as e:
            logger.error("Error checking portal status: %s", e)
            return {
                "browser_connected": False,
                "authenticated": False,
                "available_models": [],
                "session_status": "error",
                "error": str(e)
            }

    async def list_available_models(self) -> List[str]:
        """List available AI models"""
        if not self.page:
            return []

        try:
            # This is a placeholder - actual implementation depends on portal UI
            # For now, return known models
            return ["Claude Sonnet 4", "GPT-4", "Claude Haiku"]

        except Exception as e:
            logger.error("Error listing available models: %s", e)
            return []

    async def get_portal_session(self) -> Dict[str, Any]:
        """Get current portal session information"""
        if not self.page:
            return {}

        try:
            return {
                "session_id": "unknown",  # Portal-specific implementation needed
                "user_agent": await self.page.evaluate("navigator.userAgent"),
                "current_url": self.page.url,
                "page_title": await self.page.title(),
                "connected_at": self.last_health_check
            }

        except Exception as e:
            logger.error("Error getting portal session: %s", e)
            return {"error": str(e)}

    async def _check_connection_health(self):
        """Check and maintain connection health"""
        current_time = time.time()

        if current_time - self.last_health_check > self.connection_health_check_interval:
            try:
                # Simple health check - get page title
                await self.page.title()
                self.last_health_check = current_time
                logger.debug("Connection health check passed")

            except Exception as e:
                logger.error("Connection health check failed: %s", e)
                raise BrowserConnectionError(f"Connection health check failed: {e}") from e

    async def _check_authentication(self) -> bool:
        """Check if user is authenticated"""
        try:
            # Check for common authentication indicators
            # This is portal-specific and may need adjustment

            # Check if we're on a login page
            if "login" in self.page.url.lower():
                return False

            # Check for common authentication elements
            # This would need to be customized for the specific portal
            return True

        except Exception as e:
            logger.error("Error checking authentication: %s", e)
            return False

    async def close(self):
        """Clean up resources"""
        try:
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed.")
            if self.playwright_instance:
                await self.playwright_instance.stop()
                logger.info("Playwright stopped.")
        except Exception as e:
            logger.error("Error during cleanup: %s", e)

async def main():
    """Test the browser agent"""
    async with async_playwright() as playwright:
        agent = BrowserAgent()
        try:
            await agent.connect_to_browser(playwright)
            response = await agent.ask_ai("What is the capital of France?")
            print(f"Final AI Response: {response}")
        finally:
            await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
