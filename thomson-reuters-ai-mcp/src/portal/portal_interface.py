"""
Streamlined AI Portal Interface
Main orchestration class that coordinates DOM interaction, message handling, and response parsing
"""

import logging
import sys
import os
from typing import Optional, Dict, Any, List
from playwright.async_api import Page

# Add the project root to the Python path for importing exceptions
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server.exceptions import OperationTimeoutError

from .dom_interaction import DOMInteraction
from .message_handler import MessageHandler
from .response_parser import ResponseParser
from .completion_detector import CompletionDetector

logger = logging.getLogger(__name__)


class PortalInterface:
    """Main interface for Thomson Reuters AI Portal interactions"""

    def __init__(self, page: Page):
        self.page = page

        # Initialize component modules
        self.dom = DOMInteraction(page)
        self.message_handler = MessageHandler(self.dom)
        self.response_parser = ResponseParser(self.dom)
        self.completion_detector = CompletionDetector(self.dom)

        logger.info("Portal interface initialized")

    async def detect_chat_interface(self) -> bool:
        """Detect if the chat interface is available"""
        logger.info("Detecting chat interface...")
        return await self.message_handler.detect_chat_interface()

    async def select_claude_model(self, model_name: str = "Claude Sonnet 4") -> bool:
        """Select Claude model in the portal"""
        logger.info("Selecting Claude model: %s", model_name)
        return await self.message_handler.select_model(model_name)

    async def send_message(self, message: str) -> None:
        """Send a message to the AI portal"""
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        success = await self.message_handler.send_message(message)
        if not success:
            raise RuntimeError("Failed to send message to portal")

    async def wait_for_response(self, timeout: int = 60) -> str:
        """Wait for and retrieve AI response"""
        response = await self.message_handler.wait_for_response(timeout)

        if not response:
            raise OperationTimeoutError(f"No AI response received within {timeout} seconds")

        return response

    async def get_latest_response(self) -> Optional[str]:
        """Get the latest AI response without waiting"""
        return await self.response_parser.extract_latest_response()

    async def validate_response(self, response: str, question: str) -> Dict[str, Any]:
        """Validate response quality"""
        return await self.message_handler.validate_response(response, question)

    async def get_message_count(self) -> int:
        """Get current number of messages in chat"""
        return await self.message_handler.get_message_count()

    async def get_ordered_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in chronological order"""
        return await self.message_handler.get_ordered_messages()

    async def check_loading_complete(self) -> bool:
        """Check if loading indicators are gone"""
        return not await self.completion_detector._check_streaming_active()

    async def check_response_complete(self) -> bool:
        """Check if response completion indicators are present"""
        return await self.completion_detector.check_page_text_completion()

    async def take_screenshot(self, path: str = "screenshot.png") -> None:
        """Take a screenshot for debugging"""
        logger.info("Taking screenshot: %s", path)
        try:
            await self.page.screenshot(path=path, full_page=True)
            logger.info("Screenshot taken successfully")
        except Exception as e:
            logger.error("Failed to take screenshot: %s", e)
            raise

    async def get_page_info(self) -> Dict[str, Any]:
        """Get information about the current page"""
        try:
            return {
                "url": self.page.url,
                "title": await self.page.title(),
                "chat_interface_detected": await self.detect_chat_interface(),
                "message_count": await self.get_message_count(),
                "loading_complete": await self.check_loading_complete(),
            }
        except Exception as e:
            logger.error("Error getting page info: %s", e)
            return {"error": str(e)}

    async def add_custom_selector(self, selector_group: str, selector: str):
        """Add custom selector for better portal compatibility"""
        await self.dom.add_custom_selector(selector_group, selector)

    async def clear_completion_state(self):
        """Clear completion detection state"""
        await self.completion_detector.clear_completion_state()

    async def wait_for_completion(self, response_start_time: float) -> bool:
        """Wait for response completion"""
        return await self.completion_detector.wait_for_completion(response_start_time)
