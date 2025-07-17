"""
Completion detection utilities for AI portal responses
Handles detecting when AI responses are fully generated
"""

import asyncio
import logging
import time
from typing import Optional, Set
from .dom_interaction import DOMInteraction

logger = logging.getLogger(__name__)


class CompletionDetector:
    """Detects when AI responses are complete using multiple strategies"""

    def __init__(self, dom_interaction: DOMInteraction):
        self.dom = dom_interaction
        self.old_completion_indicators: Set[str] = set()
        self.last_response_check: Optional[str] = None

        # XPath patterns for cost indicators
        self.cost_xpath_patterns = [
            "//saf-metadata-item//dl[contains(text(), 'estimated query cost')]",
            "//saf-metadata-item//dl[contains(., 'estimated query cost')]",
            "//saf-metadata//dl[contains(text(), 'estimated query cost')]",
            "//saf-message-box//saf-metadata//dl[contains(., 'estimated query cost')]",
            "//dl[contains(text(), 'estimated query cost')]",
            "//dl[contains(., 'estimated query cost')]"
        ]

        # CSS selectors for cost indicators
        self.cost_css_selectors = [
            'saf-metadata-item dl',
            'saf-metadata dl',
            'saf-metadata-item',
            'saf-metadata'
        ]

        # UI indicators that suggest completion
        self.ui_completion_indicators = [
            '._copyButton_1owfm_31',
            '[class*="copyButton"]',
            '[data-testid*="copy"]',
            '[aria-label*="copy"]',
            'button:has-text("Copy")'
        ]

        # Streaming indicators that suggest response is still being generated
        self.streaming_indicators = [
            '[class*="typing"]',
            '[class*="streaming"]',
            '[class*="generating"]',
            '[aria-label*="generating"]',
            '[data-testid*="streaming"]',
            '.cursor-blink',
            '[class*="cursor"]',
            '[class*="loading"]',
            '[class*="spinner"]'
        ]

    async def wait_for_completion(self, new_response_start_time: float,
                                 min_response_time: int = 3,
                                 min_stable_time: int = 3) -> bool:
        """
        Wait for response completion using multiple detection strategies

        Args:
            new_response_start_time: When the new response started
            min_response_time: Minimum seconds for response generation
            min_stable_time: Minimum seconds response must be stable

        Returns:
            True if completion detected, False otherwise
        """
        try:
            time_since_response_start = time.time() - new_response_start_time

            # Don't check for completion too early
            if time_since_response_start < min_response_time:
                return False

            # Check for new completion indicators
            if await self._check_new_completion_indicators(new_response_start_time):
                return True

            # Check for stable response with existing indicators
            if await self._check_stable_completion(new_response_start_time, min_stable_time):
                return True

            return False

        except Exception as e:
            logger.debug("Error checking completion: %s", e)
            return False

    async def clear_completion_state(self):
        """Clear completion state to prepare for new response detection"""
        try:
            # Reset cached response state
            self.last_response_check = None
            self.old_completion_indicators = set()

            # Store current completion indicators as "old" ones to ignore
            await self._store_current_indicators()

            logger.debug("Cleared completion state, stored %d old indicators",
                         len(self.old_completion_indicators))

        except Exception as e:
            logger.debug("Error clearing completion state: %s", e)

    async def _store_current_indicators(self):
        """Store current completion indicators to ignore them later"""
        try:
            # Check XPath patterns
            for xpath in self.cost_xpath_patterns:
                try:
                    element = self.dom.page.locator(f"xpath={xpath}")
                    if await element.count() > 0:
                        text = await element.inner_text()
                        if text and 'estimated query cost' in text.lower():
                            self.old_completion_indicators.add(text.strip())
                except Exception:
                    continue

            # Check CSS selectors
            for selector in self.cost_css_selectors:
                try:
                    elements = self.dom.page.locator(selector)
                    count = await elements.count()

                    for i in range(count):
                        element = elements.nth(i)
                        text = await element.inner_text()
                        if text and 'estimated query cost' in text.lower():
                            self.old_completion_indicators.add(text.strip())
                except Exception:
                    continue

        except Exception as e:
            logger.debug("Error storing current indicators: %s", e)

    async def _check_new_completion_indicators(self, new_response_start_time: float) -> bool:
        """Check for completion indicators that appeared after response started"""
        try:
            current_indicators = set()

            # Check XPath patterns
            for xpath in self.cost_xpath_patterns:
                try:
                    element = self.dom.page.locator(f"xpath={xpath}")
                    if await element.count() > 0:
                        text = await element.inner_text()
                        if text and 'estimated query cost' in text.lower():
                            current_indicators.add(text.strip())
                except Exception:
                    continue

            # Check CSS selectors
            for selector in self.cost_css_selectors:
                try:
                    elements = self.dom.page.locator(selector)
                    count = await elements.count()

                    for i in range(count):
                        element = elements.nth(i)
                        text = await element.inner_text()
                        if text and 'estimated query cost' in text.lower():
                            current_indicators.add(text.strip())
                except Exception:
                    continue

            # Check for new indicators (not present when response started)
            new_indicators = current_indicators - self.old_completion_indicators

            if new_indicators:
                logger.debug("Found %d new completion indicators", len(new_indicators))
                return True

            # Fallback: if response has been going for a while, accept existing indicators
            time_since_response = time.time() - new_response_start_time
            if current_indicators and time_since_response >= 10:
                logger.debug("Found completion indicators after %.1fs response time",
                             time_since_response)
                return True

            return False

        except Exception as e:
            logger.debug("Error checking new completion indicators: %s", e)
            return False

    async def _check_stable_completion(self, new_response_start_time: float,
                                      min_stable_time: int) -> bool:
        """Check for completion based on response stability"""
        try:
            # Check if streaming indicators are absent
            streaming_active = await self._check_streaming_active()
            if streaming_active:
                return False

            # Check if UI completion indicators are present
            ui_indicators_present = await self._check_ui_completion_indicators()
            if not ui_indicators_present:
                return False

            # Check if enough time has passed
            time_since_response = time.time() - new_response_start_time
            if time_since_response < min_stable_time:
                return False

            logger.debug("Stable completion detected after %.1fs", time_since_response)
            return True

        except Exception as e:
            logger.debug("Error checking stable completion: %s", e)
            return False

    async def _check_streaming_active(self) -> bool:
        """Check if streaming indicators are active"""
        try:
            for indicator in self.streaming_indicators:
                try:
                    count = await self.dom.page.locator(indicator).count()
                    if count > 0:
                        logger.debug("Streaming indicator found: %s", indicator)
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.debug("Error checking streaming indicators: %s", e)
            return False

    async def _check_ui_completion_indicators(self) -> bool:
        """Check if UI completion indicators are present"""
        try:
            indicators_found = 0

            for indicator in self.ui_completion_indicators:
                try:
                    count = await self.dom.page.locator(indicator).count()
                    if count > 0:
                        indicators_found += 1
                except Exception:
                    continue

            logger.debug("Found %d UI completion indicators", indicators_found)
            return indicators_found > 0

        except Exception as e:
            logger.debug("Error checking UI completion indicators: %s", e)
            return False

    async def check_page_text_completion(self) -> bool:
        """Check for completion indicators in page text"""
        try:
            page_text = await self.dom.page.inner_text('body')
            if 'estimated query cost' in page_text.lower():
                logger.debug("Found completion indicator in page text")
                return True

            return False

        except Exception as e:
            logger.debug("Error checking page text completion: %s", e)
            return False

    async def check_response_length_stability(self, response_getter,
                                            stability_checks: int = 3) -> bool:
        """Check if response length is stable (not changing)"""
        try:
            length_history = []

            for _ in range(stability_checks):
                response = await response_getter()
                length = len(response) if response else 0
                length_history.append(length)

                if len(length_history) > 1:
                    await asyncio.sleep(1)

            # Check if last few measurements are stable
            if len(length_history) >= 2:
                last_two = length_history[-2:]
                if all(length == last_two[0] and length > 50 for length in last_two):
                    logger.debug("Response length stable at %d characters", last_two[0])
                    return True

            return False

        except Exception as e:
            logger.debug("Error checking response length stability: %s", e)
            return False
