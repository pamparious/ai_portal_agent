"""
Message handling utilities for AI portal interactions
Handles sending messages and managing message state
"""

import asyncio
import logging
import time
from typing import Optional, List, Dict, Any
from .dom_interaction import DOMInteraction
from .response_parser import ResponseParser
from .completion_detector import CompletionDetector

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles message sending and response waiting"""

    def __init__(self, dom_interaction: DOMInteraction):
        self.dom = dom_interaction
        self.response_parser = ResponseParser(dom_interaction)
        self.completion_detector = CompletionDetector(dom_interaction)

    async def send_message(self, message: str) -> bool:
        """
        Send a message to the AI portal

        Args:
            message: The message to send

        Returns:
            True if message was sent successfully, False otherwise
        """
        logger.info("Sending message: %s...", message[:50])

        try:
            # Fill the chat input
            if not await self.dom.fill_input('chat_input', message):
                logger.error("Failed to fill chat input")
                return False

            # Wait a moment for UI to update
            await asyncio.sleep(0.5)

            # Click the send button
            if not await self.dom.click_element('send_button'):
                # Fallback: try pressing Enter
                try:
                    chat_input = await self.dom.find_element('chat_input')
                    if chat_input:
                        await chat_input.press('Enter')
                        logger.info("Message sent using Enter key")
                        return True
                except Exception as e:
                    logger.error("Failed to send message with Enter key: %s", e)
                    return False

            logger.info("Message sent successfully")
            return True

        except Exception as e:
            logger.error("Error sending message: %s", e)
            return False

    async def wait_for_response(self, timeout: int = 60) -> Optional[str]:
        """
        Wait for and retrieve AI response with improved completion detection

        Args:
            timeout: Maximum time to wait for response in seconds

        Returns:
            The AI response text or None if no response received
        """
        logger.info("Waiting for response (timeout: %ds)...", timeout)

        try:
            # Get baseline state
            initial_response = await self.response_parser.extract_latest_response()
            initial_response_length = len(initial_response) if initial_response else 0

            logger.debug("Initial response length: %d", initial_response_length)

            # Clear completion state for new response
            await self.completion_detector.clear_completion_state()

            # Wait for new response
            start_time = time.time()
            new_response_detected = False
            new_response_start_time = None
            response_stable_time = None
            latest_response = None
            last_response_length = initial_response_length
            stable_length_count = 0

            min_response_time = 3  # Minimum seconds for response generation
            min_stable_time = 3   # Minimum seconds response must be stable

            while time.time() - start_time < timeout:
                try:
                    await asyncio.sleep(1)

                    # Get current response
                    current_response = await self.response_parser.extract_latest_response()
                    current_response_length = len(current_response) if current_response else 0

                    # Detect when new response starts
                    if not new_response_detected:
                        if abs(current_response_length - initial_response_length) > 50:
                            new_response_detected = True
                            new_response_start_time = time.time()
                            logger.debug("New response detected - Length: %d vs %d",
                                         current_response_length, initial_response_length)

                    # Track response progress
                    if new_response_detected and current_response:
                        latest_response = current_response.strip()

                        # Check if response length is stable
                        if current_response_length == last_response_length and current_response_length > 50:
                            stable_length_count += 1

                            if stable_length_count >= 3 and response_stable_time is None:
                                response_stable_time = time.time()
                                logger.debug("Response stable at %d characters",
                                             current_response_length)
                        else:
                            stable_length_count = 0
                            response_stable_time = None
                            if current_response_length != last_response_length:
                                logger.debug("Response length changed: %d -> %d",
                                             last_response_length, current_response_length)

                        last_response_length = current_response_length

                        # Check for completion
                        time_since_response_start = time.time() - new_response_start_time

                        if (time_since_response_start >= min_response_time and
                            response_stable_time is not None and
                            time.time() - response_stable_time >= min_stable_time):

                            # Check for completion indicators
                            if await self.completion_detector.wait_for_completion(new_response_start_time):
                                logger.info("Response complete: %s...", latest_response[:50])
                                return latest_response

                    # Progress indicator
                    elapsed = time.time() - start_time
                    if elapsed % 10 == 0:  # Log every 10 seconds
                        if new_response_detected:
                            response_time = time.time() - new_response_start_time
                            stability = f"stable for {time.time() - response_stable_time:.1f}s"
                            status = f"new response detected {response_time:.1f}s ago, length {current_response_length} ({stability})"
                        else:
                            status = "waiting for new response"
                        logger.debug("Still %s... (%.0fs elapsed)", status, elapsed)

                except Exception as e:
                    logger.debug("Error during response waiting: %s", e)
                    continue

            # Timeout handling
            if new_response_detected and latest_response:
                logger.warning("Timeout after %ds, returning response without completion confirmation",
                             timeout)
                return latest_response

            # No new response found
            logger.warning("Timeout after %ds, attempting to get any available response...", timeout)
            response = await self.response_parser.extract_latest_response()
            if response and response.strip():
                logger.info("Found response on timeout: %s...", response[:50])
                return response.strip()

            return None

        except Exception as e:
            logger.error("Error waiting for response: %s", e)
            return None

    async def get_message_count(self) -> int:
        """Get the current number of messages in the chat"""
        try:
            # Count message boxes
            message_boxes = await self.dom.find_elements('message_boxes')
            return len(message_boxes)
        except Exception as e:
            logger.debug("Error getting message count: %s", e)
            return 0

    async def get_ordered_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in chronological order with type identification"""
        messages = []

        try:
            # Get all message box texts
            message_texts = await self.dom.get_all_element_texts('message_boxes')

            for i, text in enumerate(message_texts):
                if text and len(text.strip()) > 5:
                    # Determine message type
                    if self.response_parser._is_user_message(text):
                        msg_type = 'user'
                    elif self.response_parser._is_likely_ai_response(text):
                        msg_type = 'ai'
                    else:
                        msg_type = 'unknown'

                    messages.append({
                        'text': text,
                        'type': msg_type,
                        'position': i,
                        'timestamp': time.time()
                    })

            return messages

        except Exception as e:
            logger.debug("Error getting ordered messages: %s", e)
            return []

    async def validate_response(self, response: str, question: str) -> Dict[str, Any]:
        """Validate response quality"""
        return self.response_parser.validate_response_quality(response, question)

    async def detect_chat_interface(self) -> bool:
        """Check if chat interface is available"""
        try:
            return await self.dom.check_element_exists('chat_input')
        except Exception as e:
            logger.debug("Error detecting chat interface: %s", e)
            return False

    async def select_model(self, model_name: str) -> bool:
        """
        Select AI model (placeholder for future implementation)

        Args:
            model_name: Name of the model to select

        Returns:
            True if model was selected successfully
        """
        logger.info("Selecting model: %s", model_name)

        # For now, just return True as model selection is not implemented
        # This can be extended when the portal supports model selection
        return True
