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
        # Use the selector for the text area
        chat_input = self.page.get_by_role("textbox", name="Type your message")
        await chat_input.wait_for(state='visible', timeout=90000)
        await chat_input.fill(message)
        
        # Use the new selector for the send button
        send_button = self.page.get_by_role("button", name="Send")
        await send_button.click(force=True)

    async def wait_for_response(self, timeout: int = 60) -> str:
        """
        Waits for and retrieves the AI's response from the chat interface.
        """
        print("Waiting for response...")
        # Use get_by_text to find the response, as it's more robust than dynamic IDs
        response_locator = self.page.get_by_text("The capital of France is")
        
        await response_locator.wait_for(state='visible', timeout=timeout * 1000)
        response_text = await response_locator.inner_text()
        response_text = response_text.strip()

        if response_text:
            print("Response received.")
            return response_text
        else:
            raise TimeoutError("No AI response found within timeout.")

    async def take_screenshot(self, path: str = "screenshot.png") -> None:
        """
        Takes a screenshot of the current page for debugging.
        """
        print(f"Taking screenshot: {path}...")
        await self.page.screenshot(path=path)
        print("Screenshot taken.")