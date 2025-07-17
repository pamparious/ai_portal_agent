
"""
Response parsing utilities for AI portal responses
Handles text extraction, cleaning, and validation
"""

import logging
from typing import Optional, List, Dict, Any
from .dom_interaction import DOMInteraction

logger = logging.getLogger(__name__)


class ResponseParser:
    """Handles parsing and cleaning of AI responses"""

    def __init__(self, dom_interaction: DOMInteraction):
        self.dom = dom_interaction

        # Patterns to identify UI elements that should be filtered out
        self.ui_patterns = {
            'connection_status': ['connection: ready', 'temporary chat', 'new chat'],
            'navigation': ['menu', 'ai platform', 'open arena experiences'],
            'model_info': ['claude 4 sonnet', 'claude sonnet 4'],
            'cost_info': ['estimated query cost', 'usd', 'query cost'],
            'timestamps': ['ago', 'min ago', 'hours ago', 'just now'],
            'user_info': ['ap', 'user']
        }

        # Patterns that indicate a good AI response
        self.good_response_patterns = [
            'the answer is', 'according to', 'based on', 'here is', 'here are',
            'this is', 'that is', 'i can help', 'let me', 'to answer'
        ]

        # Patterns that indicate response errors
        self.error_patterns = [
            'error', 'failed', 'could not', 'unable to',
            'something went wrong', 'try again', 'timeout'
        ]

    async def extract_latest_response(self) -> Optional[str]:
        """Extract the latest AI response from the page"""
        try:
            # Strategy 1: Get from specific AI response elements
            response = await self._extract_from_ai_elements()
            if response:
                return response

            # Strategy 2: Get from message boxes
            response = await self._extract_from_message_boxes()
            if response:
                return response

            # Strategy 3: Pattern matching in page content
            response = await self._extract_from_page_content()
            if response:
                return response

            logger.warning("No AI response found with any extraction strategy")
            return None

        except Exception as e:
            logger.error("Error extracting latest response: %s", e)
            return None

    async def _extract_from_ai_elements(self) -> Optional[str]:
        """Extract response from AI-specific elements"""
        try:
            # Get all AI response elements
            texts = await self.dom.get_all_element_texts('ai_response')

            for text in reversed(texts):  # Start with most recent
                cleaned_text = self._clean_response_text(text)
                if self._is_valid_response(cleaned_text):
                    logger.debug("Extracted response from AI elements: %s...", cleaned_text[:50])
                    return cleaned_text

            return None

        except Exception as e:
            logger.debug("Error extracting from AI elements: %s", e)
            return None

    async def _extract_from_message_boxes(self) -> Optional[str]:
        """Extract response from message box elements"""
        try:
            # Get all message box texts
            texts = await self.dom.get_all_element_texts('message_boxes')

            # Filter for AI responses (longer, non-question texts)
            ai_responses = []
            for text in texts:
                cleaned_text = self._clean_response_text(text)
                if self._is_likely_ai_response(cleaned_text):
                    ai_responses.append(cleaned_text)

            if ai_responses:
                # Return the last (most recent) AI response
                latest_response = ai_responses[-1]
                logger.debug("Extracted response from message boxes: %s...", latest_response[:50])
                return latest_response

            return None

        except Exception as e:
            logger.debug("Error extracting from message boxes: %s", e)
            return None

    async def _extract_from_page_content(self) -> Optional[str]:
        """Extract response using pattern matching in page content"""
        try:
            page_content = await self.dom.page.inner_text('body')

            # Look for response patterns
            for pattern in self.good_response_patterns:
                if pattern.lower() in page_content.lower():
                    # Extract sentences containing the pattern
                    sentences = page_content.split('.')
                    for sentence in sentences:
                        if (pattern.lower() in sentence.lower() and
                            not sentence.strip().startswith(('What', 'How', 'Why', 'When', 'Where')) and
                            not sentence.strip().endswith('?')):

                            cleaned_sentence = sentence.strip()
                            if len(cleaned_sentence) > 20:
                                logger.debug("Extracted response from page content: %s...",
                                             cleaned_sentence[:50])
                                return cleaned_sentence + '.'

            return None

        except Exception as e:
            logger.debug("Error extracting from page content: %s", e)
            return None

    def _clean_response_text(self, text: str) -> str:
        """Clean response text by removing UI elements and formatting"""
        if not text:
            return ""

        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip lines that match UI patterns
            if self._is_ui_element_line(line):
                continue

            # Skip very short lines (likely UI elements)
            if len(line) <= 3:
                continue

            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def _is_ui_element_line(self, line: str) -> bool:
        """Check if a line is likely a UI element"""
        line_lower = line.lower()

        # Check against UI patterns
        for pattern_group in self.ui_patterns.values():
            for pattern in pattern_group:
                if pattern in line_lower:
                    return True

        # Check for timestamp patterns
        if any(pattern in line_lower for pattern in ['ago', 'min ago', 'hours ago']):
            return True

        # Check for user initials or very short lines
        if len(line) <= 3 and line.isupper():
            return True

        return False

    def _is_valid_response(self, text: str) -> bool:
        """Check if text is a valid AI response"""
        if not text or len(text.strip()) < 10:
            return False

        # Check if it's not just UI elements
        if self._is_mostly_ui_elements(text):
            return False

        # Check if it's not an error message
        if self._contains_error_patterns(text):
            return False

        return True

    def _is_likely_ai_response(self, text: str) -> bool:
        """Check if text is likely an AI response based on patterns"""
        if not self._is_valid_response(text):
            return False

        text_lower = text.lower()

        # Check for AI response indicators
        for pattern in self.good_response_patterns:
            if pattern in text_lower:
                return True

        # Check if it's a declarative statement (not a question)
        if (not text.strip().endswith('?') and
            not self._is_user_message(text) and
            len(text.split()) > 8):
            return True

        return False

    def _is_mostly_ui_elements(self, text: str) -> bool:
        """Check if text is mostly UI elements"""
        words = text.split()
        ui_word_count = 0

        for word in words:
            word_lower = word.lower()
            for pattern_group in self.ui_patterns.values():
                for pattern in pattern_group:
                    if pattern in word_lower:
                        ui_word_count += 1
                        break

        # If more than 50% of words are UI-related, consider it UI
        return len(words) > 0 and (ui_word_count / len(words)) > 0.5

    def _contains_error_patterns(self, text: str) -> bool:
        """Check if text contains error patterns"""
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in self.error_patterns)

    def _is_user_message(self, text: str) -> bool:
        """Check if text is likely a user message"""
        text_lower = text.lower().strip()

        # Check for question patterns
        question_patterns = [
            'what is', 'what are', 'how to', 'how do', 'why is', 'why are',
            'where is', 'where are', 'when is', 'when are', 'who is', 'who are',
            'can you', 'could you', 'would you', 'please'
        ]

        for pattern in question_patterns:
            if pattern in text_lower:
                return True

        # Check if it ends with a question mark
        if text.strip().endswith('?'):
            return True

        return False

    def validate_response_quality(self, response: str, question: str) -> Dict[str, Any]:
        """Validate response quality and provide scoring"""
        validation_result = {
            "is_valid": True,
            "score": 0,
            "reason": "",
            "checks": {}
        }

        # Check 1: Response length
        if len(response.strip()) < 10:
            validation_result["is_valid"] = False
            validation_result["reason"] = "Response too short"
            validation_result["checks"]["length"] = False
        else:
            validation_result["checks"]["length"] = True
            validation_result["score"] += 25

        # Check 2: Content quality (not UI elements)
        if self._is_mostly_ui_elements(response):
            validation_result["is_valid"] = False
            validation_result["reason"] = "Response contains mostly UI elements"
            validation_result["checks"]["content_quality"] = False
        else:
            validation_result["checks"]["content_quality"] = True
            validation_result["score"] += 25

        # Check 3: Uniqueness (not identical to question)
        if response.lower().strip() == question.lower().strip():
            validation_result["is_valid"] = False
            validation_result["reason"] = "Response is identical to question"
            validation_result["checks"]["uniqueness"] = False
        else:
            validation_result["checks"]["uniqueness"] = True
            validation_result["score"] += 25

        # Check 4: Error-free
        if self._contains_error_patterns(response):
            validation_result["score"] -= 10
            validation_result["checks"]["error_free"] = False
        else:
            validation_result["checks"]["error_free"] = True
            validation_result["score"] += 25

        # Check 5: Proper answer indicators
        has_good_indicators = any(indicator in response.lower() for indicator in self.good_response_patterns)
        if has_good_indicators:
            validation_result["score"] += 10
            validation_result["checks"]["proper_answer"] = True
        else:
            validation_result["checks"]["proper_answer"] = False

        return validation_result
