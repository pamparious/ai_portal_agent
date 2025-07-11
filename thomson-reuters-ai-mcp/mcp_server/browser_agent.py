import asyncio
import logging
from playwright.async_api import Browser, Page, expect, async_playwright
from src.portal.portal_interface import PortalInterface

logger = logging.getLogger(__name__)

class BrowserAgent:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.portal_interface: PortalInterface = None
        self.playwright_instance = None

    async def connect_to_browser(self, playwright_instance):
        logger.info("Connecting to existing Edge browser session...")
        try:
            # Connect to an existing Edge browser instance via CDP
            # Assumes Edge is running with remote debugging enabled on port 9222
            self.browser = await playwright_instance.chromium.connect_over_cdp("http://localhost:9222")
            
            # Get the first page
            self.page = self.browser.contexts[0].pages[0]
            self.portal_interface = PortalInterface(self.page)
            logger.info(f"Connected to browser. Current URL: {self.page.url}")
            
            # Navigate to the AI portal if not already there
            expected_url_part = "dataandanalytics.int.thomsonreuters.com/ai-platform"
            if expected_url_part not in self.page.url:
                logger.info(f"Navigating to AI portal: {expected_url_part}")
                await self.page.goto("https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/27bb41d4-140b-4f8d-9179-bc57f3efbd62", timeout=30000)
                await self.page.wait_for_load_state("networkidle")
                logger.info(f"Navigated to {self.page.url}")
            
            

        except Exception as e:
            logger.error(f"Failed to connect to browser or navigate: {e}")
            raise

    async def ask_ai(self, query: str) -> str:
        if not self.page:
            raise RuntimeError("Browser not connected. Call connect_to_browser first.")

        logger.info(f"Asking AI: {query}")
        try:
            await self.portal_interface.send_message(query)
            response_text = await self.portal_interface.wait_for_response()
            logger.info(f"Received AI response: {response_text}")
            return response_text
        except Exception as e:
            logger.error(f"Error during AI interaction: {e}")
            return f"Error: {e}"

    async def close(self):
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed.")
        if self.playwright_instance:
            await self.playwright_instance.stop()
            logger.info("Playwright stopped.")

async def main():
    agent = BrowserAgent()
    try:
        await agent.connect_to_browser()
        response = await agent.ask_ai("What is the capital of France?")
        print(f"Final AI Response: {response}")
    finally:
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())