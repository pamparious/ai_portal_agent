import asyncio
from playwright.async_api import Page

class PortalInterface:
    def __init__(self, page: Page):
        self.page = page

    async def detect_chat_interface(self) -> bool:
        """
        Detects if the chat interface is visible on the page.
        """
        print("Detecting chat interface...")
        try:
            # Use Playwright's locator for better element targeting
            await self.page.locator('textarea[placeholder*="Type your message"]').wait_for(state='visible', timeout=60000)
            return True
        except Exception:
            return False

    async def select_claude_model(self, model_name: str) -> bool:
        """
        Selects the specified Claude model from the available options.
        Requires specific DOM selectors for model selection.
        """
        print(f"Selecting Claude model: {model_name}...")
        # Placeholder: Implement actual model selection here using Playwright locators
        # Example: await self.page.locator(f'div[data-model="{model_name}"]').click()
        return False

    async def send_message(self, message: str) -> None:
        """
        Sends a message to the chat interface.
        """
        print(f"Sending message: {message}...")
        chat_input = self.page.locator('textarea[placeholder*="Type your message"]')
        await chat_input.wait_for(state='visible', timeout=90000)
        await chat_input.fill(message)
        # Assuming there's a send button, or pressing Enter sends the message
        await chat_input.press('Enter')

    async def wait_for_response(self, timeout: int = 60) -> str:
        """
        Waits for and retrieves the AI's response from the chat interface.
        Requires specific DOM selectors for the response area.
        Implements retry logic.
        """
        print("Waiting for response...")
        start_time = asyncio.get_event_loop().time()
        response_selector = '.message-bubble.from-ai' # This selector needs to be confirmed
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                # Wait for at least one response bubble to appear
                await self.page.locator(response_selector).first.wait_for(state='visible', timeout=5000) # Short timeout for polling
                
                # Get all response elements and retrieve the text of the last one
                response_elements = await self.page.locator(response_selector).all_text_contents()
                if response_elements:
                    last_response_text = response_elements[-1].strip()
                    if last_response_text:
                        print("Response received.")
                        return last_response_text
            except Exception:
                pass # Continue waiting if element not found yet
            await asyncio.sleep(1) # Check every second
        raise TimeoutError("AI response not received within timeout.")

    async def take_screenshot(self, path: str = "screenshot.png") -> None:
        """
        Takes a screenshot of the current page for debugging.
        """
        print(f"Taking screenshot: {path}...")
        await self.page.screenshot(path=path)
        print("Screenshot taken.")