"""
DOM interaction utilities for the Thomson Reuters AI Portal
Handles element finding, clicking, and form interactions
"""

import asyncio
import logging
from typing import Optional, List
from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


class DOMInteraction:
    """Handles DOM element interactions with fallback strategies"""

    def __init__(self, page: Page):
        self.page = page

        # Selector groups for different UI elements
        self.selectors = {
            'chat_input': [
                'textarea[placeholder*="Type your message"]',
                'textarea[placeholder*="message"]',
                'input[placeholder*="Type your message"]',
                'textarea[aria-label*="message"]',
                '[role="textbox"]',
                'textarea',
                'input[type="text"]'
            ],
            'send_button': [
                'saf-button[aria-label*="Send"]',
                'button[aria-label*="Send"]',
                'saf-icon-button[aria-label*="Send"]',
                'button:has-text("Send")',
                'button[type="submit"]',
                '[data-testid="send-button"]',
                'button:has([class*="send"])',
                'button[title*="Send"]',
                'button:has(saf-icon[icon-name*="arrow"])',
                'button:has(saf-icon[icon-name*="send"])',
                'button:has([class*="arrow"])'
            ],
            'ai_response': [
                '[data-testid="remark-wrapper"]',
                'saf-message-box[appearance="agent"] [data-testid="remark-wrapper"]',
                'saf-message-box[appearance="agent"] p',
                '._copyButton_1owfm_31',
                'saf-message-box[appearance="agent"]'
            ],
            'metadata_cost': [
                'saf-metadata-item dl',
                'saf-metadata dl',
                'saf-metadata-item',
                'saf-metadata'
            ],
            'message_boxes': [
                'saf-message-box[appearance="user"]',
                'saf-message-box[appearance="agent"]',
                'saf-message-box'
            ]
        }

    async def find_element(self, selector_group: str, wait_time: int = 5000) -> Optional[Locator]:
        """Find an element using fallback selectors"""
        selectors = self.selectors.get(selector_group, [])

        for selector in selectors:
            try:
                element = self.page.locator(selector)
                await element.wait_for(state='visible', timeout=wait_time)
                logger.debug("Found element with selector: %s", selector)
                return element
            except Exception as e:
                logger.debug("Selector %s failed: %s", selector, e)
                continue

        logger.warning("No element found for selector group: %s", selector_group)
        return None

    async def find_elements(self, selector_group: str) -> List[Locator]:
        """Find all elements matching selector group"""
        selectors = self.selectors.get(selector_group, [])
        elements = []

        for selector in selectors:
            try:
                locator = self.page.locator(selector)
                count = await locator.count()

                if count > 0:
                    for i in range(count):
                        elements.append(locator.nth(i))

            except Exception as e:
                logger.debug("Selector %s failed: %s", selector, e)
                continue

        return elements

    async def click_element(self, selector_group: str, force: bool = False) -> bool:
        """Click an element using fallback strategies"""
        element = await self.find_element(selector_group)

        if not element:
            return False

        try:
            # Try multiple click strategies
            strategies = [
                lambda: element.click(force=force, timeout=5000),
                lambda: element.click(position={"x": 12, "y": 12}, force=True),
                lambda: element.dispatch_event("click")
            ]

            for strategy in strategies:
                try:
                    await strategy()
                    logger.debug("Successfully clicked element in group: %s", selector_group)
                    return True
                except Exception as e:
                    logger.debug("Click strategy failed: %s", e)
                    continue

            return False

        except Exception as e:
            logger.error("Failed to click element: %s", e)
            return False

    async def fill_input(self, selector_group: str, text: str) -> bool:
        """Fill input field with text"""
        element = await self.find_element(selector_group)

        if not element:
            return False

        try:
            await element.fill(text)
            logger.debug("Successfully filled input with text: %s...", text[:50])
            return True
        except Exception as e:
            logger.error("Failed to fill input: %s", e)
            return False

    async def get_element_text(self, selector_group: str, element_index: int = 0) -> Optional[str]:
        """Get text content from element"""
        elements = await self.find_elements(selector_group)

        if not elements or element_index >= len(elements):
            return None

        try:
            text = await elements[element_index].inner_text()
            return text.strip() if text else None
        except Exception as e:
            logger.debug("Failed to get text from element: %s", e)
            return None

    async def get_all_element_texts(self, selector_group: str) -> List[str]:
        """Get text content from all matching elements"""
        elements = await self.find_elements(selector_group)
        texts = []

        for element in elements:
            try:
                text = await element.inner_text()
                if text and text.strip():
                    texts.append(text.strip())
            except Exception as e:
                logger.debug("Failed to get text from element: %s", e)
                continue

        return texts

    async def wait_for_element_change(self, selector_group: str, initial_text: str,
                                     timeout: int = 30) -> bool:
        """Wait for element text to change from initial value"""
        start_time = asyncio.get_event_loop().time()

        while (asyncio.get_event_loop().time() - start_time) < timeout:
            current_text = await self.get_element_text(selector_group)

            if current_text and current_text != initial_text:
                logger.debug("Element text changed from '%s...' to '%s...'",
                             initial_text[:50], current_text[:50])
                return True

            await asyncio.sleep(1)

        return False

    async def check_element_exists(self, selector_group: str) -> bool:
        """Check if element exists without waiting"""
        selectors = self.selectors.get(selector_group, [])

        for selector in selectors:
            try:
                count = await self.page.locator(selector).count()
                if count > 0:
                    return True
            except Exception:
                continue

        return False

    async def add_custom_selector(self, selector_group: str, selector: str):
        """Add custom selector to existing group"""
        if selector_group not in self.selectors:
            self.selectors[selector_group] = []

        if selector not in self.selectors[selector_group]:
            self.selectors[selector_group].insert(0, selector)  # Add at beginning for priority
            logger.debug("Added custom selector '%s' to group '%s'",
                         selector, selector_group)
