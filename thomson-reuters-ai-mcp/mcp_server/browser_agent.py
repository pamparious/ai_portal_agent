import asyncio
import logging
from playwright.async_api import Browser, Page, expect, async_playwright

logger = logging.getLogger(__name__)

class BrowserAgent:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None

    async def connect_to_browser(self, playwright_instance):
        logger.info("Connecting to existing Edge browser session...")
        try:
            # Connect to an existing Edge browser instance via CDP
            # Assumes Edge is running with remote debugging enabled on port 9222
            self.browser = await playwright_instance.chromium.connect_over_cdp("http://localhost:9222")
            
            # Get the first page
            self.page = self.browser.contexts[0].pages[0]
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
            logger.info("Locating chat input field...")
            chat_input = self.page.locator("textarea[placeholder='Type your message']")
            await expect(chat_input).to_be_visible(timeout=10000)
            logger.info("Filling chat input field...")
            await chat_input.fill(query)
            
            logger.info("Locating send button...")
            send_button = self.page.locator("saf-button[data-testid='chat-send-btn']")
            await expect(send_button).to_be_visible(timeout=5000)
            logger.info("Clicking send button...")
            await send_button.click()

            logger.info("Waiting for AI response paragraph...")
            ai_response_paragraph = self.page.locator("saf-message-box[appearance='agent'] div[data-testid='remark-wrapper'] p").last
            await expect(ai_response_paragraph).to_be_visible(timeout=60000)
            logger.info("AI response paragraph visible. Extracting text...")
            
            response_text = await ai_response_paragraph.inner_text()
            response_text = response_text.strip()
            if response_text:
                logger.info(f"Received AI response: {response_text}")
                return response_text
            else:
                logger.warning("No AI response found.")
                return "No response received."

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