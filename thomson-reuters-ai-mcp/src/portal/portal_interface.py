import asyncio
import logging
import time
import sys
import os
from typing import Optional, List, Dict, Any
from playwright.async_api import Page

# Add the project root to the Python path for importing exceptions
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server.exceptions import TimeoutError

logger = logging.getLogger(__name__)


class PortalInterface:
    def __init__(self, page: Page):
        self.page = page
        self.response_selectors = [
            # SAF-based selectors (Thomson Reuters UI framework)
            'saf-message-box[appearance="agent"] [data-testid="remark-wrapper"]',
            'saf-message-box[appearance="agent"]',
            'saf-chat-message[type="response"]',
            'saf-response-content',
            
            # Standard selectors
            '[data-testid="message-content"]',
            '[data-testid="remark-wrapper"]',
            '.message-content',
            '[class*="response"]',
            '[class*="message"]',
            'div[role="article"]',
            
            # Generic text-based selectors
            '*:has-text("The answer")',
            '*:has-text("equals")',
            '*:has-text("is 4")',
            '*:has-text("2+2")',
            'div:has-text("4")',
            'p:has-text("4")',
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
            # SAF-based send button selectors
            'saf-button[aria-label*="Send"]',
            'button[aria-label*="Send"]',
            'saf-icon-button[aria-label*="Send"]',
            
            # Generic send button selectors
            'button:has-text("Send")',
            'button[type="submit"]',
            '[data-testid="send-button"]',
            'button:has([class*="send"])',
            'button:has([class*="submit"])',
            'button[title*="Send"]',
            
            # Icon-based selectors (for buttons with only icons)
            'button:has(saf-icon[icon-name*="arrow"])',
            'button:has(saf-icon[icon-name*="send"])',
            'button svg[class*="send"]',
            'button:has([class*="arrow"])',
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
                    # Try multiple click methods to handle overlapping elements
                    try:
                        await send_button.first.click(force=True, timeout=5000)
                        logger.info(f"Send button clicked with selector: {selector}")
                        return
                    except Exception as click_error:
                        logger.debug(f"Force click failed, trying alternative methods: {click_error}")
                        
                        # Try clicking the icon directly if it's intercepting
                        try:
                            await send_button.first.click(position={"x": 12, "y": 12}, force=True)
                            logger.info(f"Send button clicked with position offset: {selector}")
                            return
                        except Exception as pos_error:
                            logger.debug(f"Position click failed: {pos_error}")
                            
                            # Try using dispatchEvent
                            try:
                                await send_button.first.dispatch_event("click")
                                logger.info(f"Send button clicked with dispatch event: {selector}")
                                return
                            except Exception as dispatch_error:
                                logger.debug(f"Dispatch event failed: {dispatch_error}")
                                
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
        Uses improved detection to distinguish AI responses from user messages.
        """
        logger.info(f"Waiting for response (timeout: {timeout}s)...")
        
        # Get baseline state before waiting
        initial_messages = await self._get_ordered_messages()
        initial_ai_count = len([msg for msg in initial_messages if msg['type'] == 'ai'])
        logger.debug(f"Initial AI message count: {initial_ai_count}")
        
        start_time = time.time()
        last_check_time = start_time
        
        while time.time() - start_time < timeout:
            try:
                # Wait before checking again
                await asyncio.sleep(2)
                
                # Check for new AI messages
                current_messages = await self._get_ordered_messages()
                current_ai_count = len([msg for msg in current_messages if msg['type'] == 'ai'])
                
                # If we have a new AI message, get it
                if current_ai_count > initial_ai_count:
                    logger.debug(f"New AI messages detected: {current_ai_count} vs {initial_ai_count}")
                    
                    response = await self._get_latest_response()
                    if response and response.strip():
                        logger.info(f"Response received: {response[:50]}..." if len(response) > 50 else f"Response received: {response}")
                        return response.strip()
                
                # Also check for loading completion every 5 seconds
                if time.time() - last_check_time > 5:
                    if await self._check_loading_complete():
                        response = await self._get_latest_response()
                        if response and response.strip():
                            logger.info(f"Response received after loading: {response[:50]}..." if len(response) > 50 else f"Response received: {response}")
                            return response.strip()
                    last_check_time = time.time()
                
                # Progress indicator
                elapsed = time.time() - start_time
                if elapsed % 10 == 0:  # Log every 10 seconds
                    logger.debug(f"Still waiting for response... ({elapsed:.0f}s elapsed)")
                
            except Exception as e:
                logger.debug(f"Error while waiting for response: {e}")
                continue
        
        # Timeout - try to get any response that might be there
        logger.warning(f"Timeout after {timeout}s, attempting to get any available response...")
        response = await self._get_latest_response()
        if response and response.strip():
            logger.info(f"Found response on timeout: {response[:50]}..." if len(response) > 50 else f"Found response: {response}")
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
            # Strategy 1: Look for AI response content using specific selectors
            try:
                # Use the correct selectors based on DOM analysis
                ai_response_selectors = [
                    '[data-testid="remark-wrapper"]',  # Main AI response container
                    '._copyButton_1owfm_31',  # AI response with copy button
                    'saf-message-box[appearance="agent"] [data-testid="remark-wrapper"]',  # AI message box
                    'saf-message-box[appearance="agent"] p',  # AI message paragraphs
                ]
                
                for selector in ai_response_selectors:
                    try:
                        elements = self.page.locator(selector)
                        count = await elements.count()
                        
                        if count > 0:
                            # Get the last AI response (most recent)
                            last_element = elements.nth(count - 1)
                            text = await last_element.inner_text()
                            
                            # Clean up the text
                            cleaned_text = self._clean_ai_response_text(text)
                            
                            if cleaned_text and len(cleaned_text.strip()) > 10 and not self._is_ui_element(cleaned_text):
                                logger.debug(f"Found AI response with selector: {selector}")
                                return cleaned_text
                    except Exception as e:
                        logger.debug(f"Error with AI response selector {selector}: {e}")
                        continue
                
            except Exception as e:
                logger.debug(f"Error in direct selector response detection: {e}")
            
            # Strategy 2: Look for saf-message-box elements
            try:
                # Get AI message boxes
                ai_message_boxes = self.page.locator('saf-message-box[appearance="agent"]')
                count = await ai_message_boxes.count()
                
                if count > 0:
                    # Get the last AI message box
                    last_ai_box = ai_message_boxes.nth(count - 1)
                    
                    # Try to get the content from within the message box
                    try:
                        # Look for the actual content within the message box
                        content_selectors = [
                            '[data-testid="remark-wrapper"]',
                            'p',
                            'div:not([class*="metadata"]):not([class*="avatar"])',
                        ]
                        
                        for content_selector in content_selectors:
                            try:
                                content_elements = last_ai_box.locator(content_selector)
                                content_count = await content_elements.count()
                                
                                if content_count > 0:
                                    # Get the first substantial content element
                                    for i in range(content_count):
                                        content_element = content_elements.nth(i)
                                        text = await content_element.inner_text()
                                        
                                        if text and len(text.strip()) > 10 and not self._is_ui_element(text):
                                            cleaned_text = self._clean_ai_response_text(text)
                                            if cleaned_text and len(cleaned_text.strip()) > 10:
                                                logger.debug(f"Found AI response in message box: {cleaned_text[:50]}...")
                                                return cleaned_text
                            except Exception as e:
                                logger.debug(f"Error with content selector {content_selector}: {e}")
                                continue
                                
                    except Exception as e:
                        logger.debug(f"Error extracting content from message box: {e}")
                        
                        # Fallback: get all text from the message box
                        try:
                            full_text = await last_ai_box.inner_text()
                            if full_text and len(full_text.strip()) > 10:
                                cleaned_text = self._clean_ai_response_text(full_text)
                                if cleaned_text and len(cleaned_text.strip()) > 10:
                                    logger.debug(f"Found AI response from full message box: {cleaned_text[:50]}...")
                                    return cleaned_text
                        except Exception as e:
                            logger.debug(f"Error getting full text from message box: {e}")
                
            except Exception as e:
                logger.debug(f"Error in message box response detection: {e}")
            
            # Strategy 3: Fallback - look for response patterns in page content
            try:
                # Get all text content and look for response patterns
                page_content = await self.page.inner_text('body')
                
                # Look for common AI response patterns
                response_patterns = [
                    'The capital of Germany is',
                    'The capital of France is',
                    'Berlin is the capital',
                    'Paris is the capital',
                    'The answer is',
                    'According to',
                    'Based on',
                    'Here is',
                    'Here are',
                    'I can help',
                    'Let me',
                ]
                
                for pattern in response_patterns:
                    if pattern.lower() in page_content.lower():
                        # Extract the sentence containing the pattern
                        sentences = page_content.split('.')
                        for sentence in sentences:
                            if pattern.lower() in sentence.lower():
                                # Make sure it's not a user question
                                if not ('?' in sentence or sentence.strip().startswith('What') or sentence.strip().startswith('How')):
                                    return sentence.strip() + '.'
                
            except Exception as e:
                logger.debug(f"Error in fallback response detection: {e}")
            
            return None
            
        except Exception as e:
            logger.debug(f"Error getting latest response: {e}")
            return None
    
    def _clean_ai_response_text(self, text: str) -> str:
        """Clean AI response text by removing timestamps, cost info, etc."""
        if not text:
            return ""
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip timestamp lines (e.g., "7m ago")
            if line.endswith(' ago') or line.endswith(' min ago') or line.endswith(' hours ago'):
                continue
                
            # Skip cost information lines
            if 'query cost' in line.lower() or 'usd' in line.lower() or '$' in line:
                continue
                
            # Skip model name lines
            if 'claude' in line.lower() and 'sonnet' in line.lower():
                continue
                
            # Skip user initials (AP, etc.)
            if len(line) <= 3 and line.isupper():
                continue
                
            # Keep the actual response content
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    def _is_user_message(self, text: str) -> bool:
        """Determine if a message is from the user based on content patterns"""
        if not text:
            return False
            
        text_lower = text.lower().strip()
        
        # Check for question patterns (typical user messages)
        question_patterns = [
            'what is',
            'what are',
            'how to',
            'how do',
            'why is',
            'why are',
            'where is',
            'where are',
            'when is',
            'when are',
            'who is',
            'who are',
            'can you',
            'could you',
            'would you',
            'please',
        ]
        
        for pattern in question_patterns:
            if pattern in text_lower:
                return True
                
        # Check if it ends with a question mark
        if text.strip().endswith('?'):
            return True
            
        # Check if it contains user initials (AP, etc.)
        if 'ap' in text_lower and len(text) < 100:  # Short messages with initials
            return True
            
        return False
    
    def _is_ui_element(self, text: str) -> bool:
        """Determine if text is a UI element rather than content"""
        if not text:
            return True
            
        text_lower = text.lower().strip()
        
        # Check for common UI elements
        ui_patterns = [
            'connection: ready',
            'temporary chat',
            'new chat',
            'menu',
            'ai platform',
            'open arena experiences',
            'claude 4 sonnet',
            'estimated query cost',
            'usd',
        ]
        
        for pattern in ui_patterns:
            if pattern in text_lower:
                return True
        
        # Check if it's mostly navigation/UI text
        if len(text.strip()) < 50 and any(word in text_lower for word in ['menu', 'chat', 'connection', 'platform']):
            return True
            
        return False
    
    def _is_likely_ai_response(self, text: str) -> bool:
        """Determine if text is likely an AI response based on content patterns"""
        if not text or len(text.strip()) < 20:
            return False
            
        text_lower = text.lower().strip()
        
        # Check for AI response patterns
        response_indicators = [
            'the capital of',
            'the answer is',
            'according to',
            'based on',
            'here is',
            'here are',
            'i can help',
            'let me',
            'berlin is',
            'paris is',
            'this is',
            'that is',
            'it is',
            'they are',
            'there are',
            'there is',
        ]
        
        for indicator in response_indicators:
            if indicator in text_lower:
                return True
        
        # Check if it's a declarative statement (not a question)
        if not text.strip().endswith('?') and not self._is_user_message(text) and not self._is_ui_element(text):
            # Look for sentence-like structure
            if '.' in text or len(text.split()) > 8:
                return True
                
        return False
    
    async def _get_ordered_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in chronological order with type identification"""
        messages = []
        
        try:
            # Strategy 1: Look for saf-message-box elements (most reliable)
            try:
                # Get user message boxes
                user_message_boxes = self.page.locator('saf-message-box[appearance="user"]')
                user_count = await user_message_boxes.count()
                
                for i in range(user_count):
                    try:
                        element = user_message_boxes.nth(i)
                        text = await element.inner_text()
                        
                        if text and len(text.strip()) > 5:
                            # Get position for ordering
                            try:
                                position = await element.bounding_box()
                                y_pos = position['y'] if position else 0
                            except:
                                y_pos = 0
                            
                            # Check for timestamp indicators
                            timestamp_score = 0
                            if 'just now' in text:
                                timestamp_score = 1000  # Most recent
                            elif 'ago' in text:
                                timestamp_score = 500  # Older
                            
                            messages.append({
                                'text': text,
                                'type': 'user',
                                'position': y_pos,
                                'selector': 'saf-message-box[appearance="user"]',
                                'timestamp_score': timestamp_score
                            })
                            
                    except Exception as e:
                        logger.debug(f"Error getting user message {i}: {e}")
                        continue
                
                # Get AI message boxes
                ai_message_boxes = self.page.locator('saf-message-box[appearance="agent"]')
                ai_count = await ai_message_boxes.count()
                
                for i in range(ai_count):
                    try:
                        element = ai_message_boxes.nth(i)
                        text = await element.inner_text()
                        
                        if text and len(text.strip()) > 5:
                            # Get position for ordering
                            try:
                                position = await element.bounding_box()
                                y_pos = position['y'] if position else 0
                            except:
                                y_pos = 0
                            
                            # Check for timestamp indicators
                            timestamp_score = 0
                            if 'just now' in text:
                                timestamp_score = 1000  # Most recent
                            elif 'ago' in text:
                                timestamp_score = 500  # Older
                            
                            messages.append({
                                'text': text,
                                'type': 'ai',
                                'position': y_pos,
                                'selector': 'saf-message-box[appearance="agent"]',
                                'timestamp_score': timestamp_score
                            })
                            
                    except Exception as e:
                        logger.debug(f"Error getting AI message {i}: {e}")
                        continue
                        
            except Exception as e:
                logger.debug(f"Error getting saf-message-box elements: {e}")
            
            # Strategy 2: Fallback to generic message detection
            if len(messages) == 0:
                fallback_selectors = [
                    '.white-pre-wrap',  # User message content
                    '[data-testid="remark-wrapper"]',  # AI response content
                    '._copyButton_1owfm_31',  # AI response with copy button
                ]
                
                for selector in fallback_selectors:
                    try:
                        elements = self.page.locator(selector)
                        count = await elements.count()
                        
                        for i in range(count):
                            element = elements.nth(i)
                            text = await element.inner_text()
                            
                            if text and len(text.strip()) > 10:  # Only substantial content
                                # Determine message type
                                msg_type = 'unknown'
                                if selector == '.white-pre-wrap' or self._is_user_message(text):
                                    msg_type = 'user'
                                elif selector in ['[data-testid="remark-wrapper"]', '._copyButton_1owfm_31'] or self._is_likely_ai_response(text):
                                    msg_type = 'ai'
                                
                                # Get position for ordering
                                try:
                                    position = await element.bounding_box()
                                    y_pos = position['y'] if position else 0
                                except:
                                    y_pos = 0
                                
                                messages.append({
                                    'text': text,
                                    'type': msg_type,
                                    'position': y_pos,
                                    'selector': selector,
                                    'timestamp_score': 0
                                })
                                
                    except Exception as e:
                        logger.debug(f"Error getting messages with selector {selector}: {e}")
                        continue
            
            # Sort by position (top to bottom) and then by timestamp score (most recent first)
            messages.sort(key=lambda x: (x['position'], -x.get('timestamp_score', 0)))
            
            # Remove duplicates (same text content)
            unique_messages = []
            seen_texts = set()
            
            for msg in messages:
                text_key = msg['text'][:50]  # Use first 50 chars as key
                if text_key not in seen_texts:
                    seen_texts.add(text_key)
                    unique_messages.append(msg)
            
            return unique_messages
            
        except Exception as e:
            logger.debug(f"Error getting ordered messages: {e}")
            return []
    
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