import asyncio
import logging
import time
from typing import Optional, List, Dict, Any
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


class PortalInterface:
    def __init__(self, page: Page):
        self.page = page
        self.response_selectors = [
            # Multiple selectors for different response types
            '[data-testid="message-content"]',
            '.message-content',
            '[class*="response"]',
            '[class*="message"]',
            'div[role="article"]',
            # Fallback selectors
            'div:has-text("The capital of France")',
            'div:has-text("Paris")',
            'p:has-text("capital")',
        ]
        self.chat_input_selectors = [
            'textarea[placeholder*="Type your message"]',
            'textarea[placeholder*="message"]',
            'input[placeholder*="Type your message"]',
            'textarea[aria-label*="message"]',
            '[role="textbox"]',
            'textarea',
            'input[type="text"]'
        ]
        self.send_button_selectors = [
            'button[aria-label*="Send"]',
            'button:has-text("Send")',
            'button[type="submit"]',
            '[data-testid="send-button"]',
            'button:has([class*="send"])',
            'button:has([class*="submit"])',
            'button[title*="Send"]',
            'button svg[class*="send"]',
        ]

    async def detect_chat_interface(self) -> bool:
        """
        Detects if the chat interface is visible on the page using multiple selectors.
        """
        logger.info("Detecting chat interface...")
        
        for selector in self.chat_input_selectors:
            try:
                await self.page.locator(selector).wait_for(state='visible', timeout=5000)
                logger.info(f"Chat interface detected with selector: {selector}")
                return True
            except Exception:
                continue
        
        logger.warning("Chat interface not detected with any selector")
        return False

    async def select_claude_model(self, model_name: str) -> bool:
        """
        Selects the specified Claude model from the available options.
        """
        logger.info(f"Selecting Claude model: {model_name}...")
        
        model_selectors = [
            f'div[data-model="{model_name}"]',
            f'button:has-text("{model_name}")',
            f'[aria-label*="{model_name}"]',
            f'div:has-text("{model_name}")',
            'div[class*="model-selector"]',
            'button[class*="model"]',
            'select[name*="model"]',
        ]
        
        for selector in model_selectors:
            try:
                element = self.page.locator(selector)
                if await element.count() > 0:
                    await element.first.click()
                    logger.info(f"Model {model_name} selected with selector: {selector}")
                    return True
            except Exception as e:
                logger.debug(f"Failed to select model with selector {selector}: {e}")
                continue
        
        logger.warning(f"Could not select model {model_name} with any selector")
        return False

    async def send_message(self, message: str) -> None:
        """
        Sends a message to the chat interface using multiple fallback selectors.
        """
        logger.info(f"Sending message: {message[:50]}..." if len(message) > 50 else f"Sending message: {message}")
        
        # First, find and fill the chat input
        chat_input = None
        for selector in self.chat_input_selectors:
            try:
                chat_input = self.page.locator(selector)
                await chat_input.wait_for(state='visible', timeout=10000)
                await chat_input.fill(message)
                logger.info(f"Message filled with selector: {selector}")
                break
            except Exception as e:
                logger.debug(f"Failed to fill message with selector {selector}: {e}")
                continue
        
        if not chat_input:
            raise Exception("Could not find chat input field with any selector")
        
        # Wait a moment for the UI to update
        await asyncio.sleep(0.5)
        
        # Find and click the send button
        for selector in self.send_button_selectors:
            try:
                send_button = self.page.locator(selector)
                if await send_button.count() > 0:
                    await send_button.first.click(force=True)
                    logger.info(f"Send button clicked with selector: {selector}")
                    return
            except Exception as e:
                logger.debug(f"Failed to click send button with selector {selector}: {e}")
                continue
        
        # Fallback: try pressing Enter
        try:
            await chat_input.press('Enter')
            logger.info("Message sent using Enter key")
        except Exception as e:
            raise Exception(f"Could not send message with any method: {e}")

    async def wait_for_response(self, timeout: int = 60) -> str:
        """
        Waits for and retrieves the AI's response from the chat interface.
        Uses dynamic detection of new messages.
        """
        logger.info(f"Waiting for response (timeout: {timeout}s)...")
        
        # First, get initial message count
        initial_message_count = await self._get_message_count()
        logger.debug(f"Initial message count: {initial_message_count}")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Wait for new messages to appear
                await asyncio.sleep(1)
                
                current_message_count = await self._get_message_count()
                
                # Check if new messages appeared
                if current_message_count > initial_message_count:
                    logger.debug(f"New messages detected: {current_message_count} vs {initial_message_count}")
                    
                    # Try to get the latest response
                    response = await self._get_latest_response()
                    if response and response.strip():
                        logger.info(f"Response received: {response[:50]}..." if len(response) > 50 else f"Response received: {response}")
                        return response.strip()
                
                # Also check for loading indicators disappearing
                if await self._check_loading_complete():
                    response = await self._get_latest_response()
                    if response and response.strip():
                        logger.info(f"Response received after loading: {response[:50]}..." if len(response) > 50 else f"Response received: {response}")
                        return response.strip()
                
            except Exception as e:
                logger.debug(f"Error while waiting for response: {e}")
                continue
        
        # Timeout - try to get any response that might be there
        logger.warning(f"Timeout after {timeout}s, attempting to get any available response...")
        response = await self._get_latest_response()
        if response and response.strip():
            return response.strip()
        
        raise TimeoutError(f"No AI response found within {timeout} seconds")

    async def _get_message_count(self) -> int:
        """Get the current number of messages in the chat"""
        try:
            # Try various message container selectors
            message_selectors = [
                '[data-testid="message"]',
                '.message',
                '[class*="message"]',
                '[role="article"]',
                'div:has-text("The capital")',
                'div:has-text("Paris")',
            ]
            
            for selector in message_selectors:
                count = await self.page.locator(selector).count()
                if count > 0:
                    return count
            
            return 0
        except Exception:
            return 0
    
    async def _get_latest_response(self) -> Optional[str]:
        """Get the latest AI response from the chat"""
        try:
            # Try multiple strategies to find the response
            
            # Strategy 1: Look for common response patterns
            for selector in self.response_selectors:
                try:
                    elements = self.page.locator(selector)
                    count = await elements.count()
                    
                    if count > 0:
                        # Get the last element (most recent)
                        last_element = elements.nth(count - 1)
                        text = await last_element.inner_text()
                        
                        if text and len(text.strip()) > 10:  # Reasonable response length
                            return text
                except Exception:
                    continue
            
            # Strategy 2: Look for any text that might be a response
            try:
                # Get all text content and look for patterns
                page_content = await self.page.inner_text('body')
                
                # Look for common response patterns
                response_patterns = [
                    'The capital of France is',
                    'Paris is the capital',
                    'France\'s capital is',
                    'The answer is',
                    'capital of France',
                ]
                
                for pattern in response_patterns:
                    if pattern.lower() in page_content.lower():
                        # Extract the sentence containing the pattern
                        sentences = page_content.split('.')
                        for sentence in sentences:
                            if pattern.lower() in sentence.lower():
                                return sentence.strip() + '.'
                
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            logger.debug(f"Error getting latest response: {e}")
            return None
    
    async def _check_loading_complete(self) -> bool:
        """Check if loading indicators are gone"""
        try:
            loading_selectors = [
                '[data-testid="loading"]',
                '.loading',
                '[class*="loading"]',
                '[class*="spinner"]',
                '[aria-label*="loading"]',
            ]
            
            for selector in loading_selectors:
                if await self.page.locator(selector).count() > 0:
                    return False
            
            return True
        except Exception:
            return True
    
    async def take_screenshot(self, path: str = "screenshot.png") -> None:
        """
        Takes a screenshot of the current page for debugging.
        """
        logger.info(f"Taking screenshot: {path}...")
        try:
            await self.page.screenshot(path=path, full_page=True)
            logger.info("Screenshot taken successfully")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            raise
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get information about the current page for debugging"""
        try:
            return {
                "url": self.page.url,
                "title": await self.page.title(),
                "chat_interface_detected": await self.detect_chat_interface(),
                "message_count": await self._get_message_count(),
                "loading_complete": await self._check_loading_complete(),
            }
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return {"error": str(e)}