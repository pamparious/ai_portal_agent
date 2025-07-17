#!/usr/bin/env python3
"""
Interactive test for MCP AI Portal Agent
Takes a question from terminal input and returns AI portal response
Enhanced with debugging capabilities and response validation
"""

import asyncio
import logging
import sys
import os
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, Any, List

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server.browser_agent import BrowserAgent
from mcp_server.exceptions import BrowserConnectionError, PortalError, AuthenticationError, OperationTimeoutError
from playwright.async_api import async_playwright

# Configure logging with different levels for different modes
def setup_logging(debug_mode: bool = False, verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug_mode else (logging.INFO if verbose else logging.WARNING)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Setup file handler for debugging
    if debug_mode:
        file_handler = logging.FileHandler('ai_portal_debug.log')
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
    
    # Configure root logger
    logging.getLogger().setLevel(level)
    logging.getLogger().addHandler(console_handler)
    
    # Set specific loggers
    logging.getLogger('mcp_server').setLevel(level)
    logging.getLogger('src.portal').setLevel(level)
    
    return logging.getLogger(__name__)

class InteractiveQueryTest:
    """Interactive test for AI Portal Agent functionality"""
    
    def __init__(self, debug_mode: bool = False, test_mode: bool = False):
        self.browser_agent = BrowserAgent()
        self.playwright_instance = None
        self.debug_mode = debug_mode
        self.test_mode = test_mode
        self.logger = logging.getLogger(__name__)
        self.test_questions = [
            "What is the capital of France?",
            "Explain quantum computing in simple terms",
            "What are the benefits of renewable energy?",
            "How does artificial intelligence work?",
            "What is the current weather like?"
        ]
        self.response_metrics = {
            "total_queries": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "average_response_time": 0,
            "response_times": []
        }
        
    async def setup(self):
        """Initialize the test environment"""
        print("[*] Setting up AI Portal Agent...")
        try:
            self.playwright_instance = await async_playwright().start()
            self.logger.info("Playwright instance started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to setup test environment: {e}")
            return False
    
    async def connect_to_browser(self):
        """Connect to browser"""
        print("[*] Connecting to browser...")
        try:
            await self.browser_agent.connect_to_browser(self.playwright_instance)
            print("[+] Browser connection successful")
            return True
        except BrowserConnectionError as e:
            print(f"[-] Browser connection failed: {e}")
            print("\n[!] Make sure to start your browser with debugging enabled:")
            print("   For Chrome: start-chrome-debug.bat")
            print("   For Edge: start-edge-debug.bat")
            return False
        except Exception as e:
            print(f"[-] Unexpected error during browser connection: {e}")
            return False
    
    async def check_portal_status(self):
        """Check if we can access the AI portal"""
        print("[*] Checking AI portal status...")
        try:
            # Use the browser agent's check_portal_status method for comprehensive status check
            status = await self.browser_agent.check_portal_status()
            
            if status["browser_connected"]:
                print(f"[*] Current page: {status.get('portal_url', 'unknown')}")
                
                if status["authenticated"]:
                    print("[+] Connected to Thomson Reuters AI portal and authenticated")
                    available_models = status.get("available_models", [])
                    if available_models:
                        print(f"[*] Available models: {', '.join(available_models)}")
                    return True
                else:
                    print("[!] Connected but not authenticated")
                    return False
            else:
                print("[-] Browser not connected")
                if "error" in status:
                    print(f"[-] Error: {status['error']}")
                return False
        except Exception as e:
            print(f"[-] Portal check failed: {e}")
            return False
    
    async def get_user_question(self):
        """Get question from user input"""
        print("\n" + "="*60)
        print("AI PORTAL QUERY INTERFACE")
        print("="*60)
        print("Enter your question for the AI portal (or 'quit' to exit):")
        
        try:
            question = input("[?] Question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                return None
            
            if not question:
                print("[!] Empty question. Please try again.")
                return await self.get_user_question()
            
            return question
            
        except KeyboardInterrupt:
            print("\n[*] Goodbye!")
            return None
        except Exception as e:
            print(f"[-] Error getting user input: {e}")
            return None
    
    async def submit_question(self, question: str) -> Optional[str]:
        """Submit question to AI portal and get response with enhanced validation"""
        print(f"[*] Submitting question: '{question}'")
        print("[*] Please wait for AI response...")
        
        start_time = time.time()
        self.response_metrics["total_queries"] += 1
        
        try:
            # Use the browser agent's ask_ai method which handles the full workflow
            response = await self.browser_agent.ask_ai(question)
            
            # Calculate response time
            response_time = time.time() - start_time
            self.response_metrics["response_times"].append(response_time)
            
            if response:
                # Validate response quality
                validation_result = self._validate_response(response, question)
                
                if validation_result["is_valid"]:
                    print("[+] Response received successfully")
                    self.response_metrics["successful_responses"] += 1
                    
                    if self.debug_mode:
                        print(f"[DEBUG] Response time: {response_time:.2f}s")
                        print(f"[DEBUG] Response length: {len(response)} characters")
                        print(f"[DEBUG] Validation: {validation_result}")
                    
                    return response
                else:
                    print(f"[!] Response validation failed: {validation_result['reason']}")
                    self.response_metrics["failed_responses"] += 1
                    
                    if self.debug_mode:
                        print(f"[DEBUG] Invalid response: {response[:100]}...")
                    
                    return None
            else:
                print("[-] No response received from portal")
                self.response_metrics["failed_responses"] += 1
                return None
                
        except PortalError as e:
            print(f"[-] Portal error: {e}")
            self.response_metrics["failed_responses"] += 1
            if self.debug_mode:
                self.logger.exception("Portal error details:")
            return None
        except OperationTimeoutError as e:
            print(f"[-] Timeout error: {e}")
            print("[!] The AI might be taking longer than expected. Try a simpler question.")
            self.response_metrics["failed_responses"] += 1
            if self.debug_mode:
                self.logger.exception("Timeout error details:")
            return None
        except ValueError as e:
            print(f"[-] Invalid input: {e}")
            self.response_metrics["failed_responses"] += 1
            if self.debug_mode:
                self.logger.exception("ValueError details:")
            return None
        except RuntimeError as e:
            print(f"[-] Runtime error: {e}")
            self.response_metrics["failed_responses"] += 1
            if self.debug_mode:
                self.logger.exception("Runtime error details:")
            return None
        except Exception as e:
            print(f"[-] Unexpected error: {e}")
            self.response_metrics["failed_responses"] += 1
            if self.debug_mode:
                self.logger.exception("Unexpected error details:")
            return None
    
    def _validate_response(self, response: str, question: str) -> Dict[str, Any]:
        """Validate the quality and completeness of the AI response"""
        validation_result = {
            "is_valid": True,
            "reason": "",
            "score": 0,
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
        
        # Check 2: Response contains actual content (not just UI elements)
        ui_patterns = [
            "connection: ready",
            "temporary chat",
            "new chat",
            "menu",
            "estimated query cost",
            "claude 4 sonnet",
            "open arena experiences"
        ]
        
        if any(pattern in response.lower() for pattern in ui_patterns):
            validation_result["is_valid"] = False
            validation_result["reason"] = "Response contains UI elements"
            validation_result["checks"]["content_quality"] = False
        else:
            validation_result["checks"]["content_quality"] = True
            validation_result["score"] += 25
        
        # Check 3: Response is not just a repetition of the question
        if response.lower().strip() == question.lower().strip():
            validation_result["is_valid"] = False
            validation_result["reason"] = "Response is identical to question"
            validation_result["checks"]["uniqueness"] = False
        else:
            validation_result["checks"]["uniqueness"] = True
            validation_result["score"] += 25
        
        # Check 4: Response doesn't contain obvious error messages
        error_patterns = [
            "error",
            "failed",
            "could not",
            "unable to",
            "something went wrong",
            "try again"
        ]
        
        contains_errors = any(pattern in response.lower() for pattern in error_patterns)
        if contains_errors:
            validation_result["score"] -= 10
            validation_result["checks"]["error_free"] = False
        else:
            validation_result["checks"]["error_free"] = True
            validation_result["score"] += 25
        
        # Check 5: Response appears to be a proper answer
        good_indicators = [
            "the answer is",
            "according to",
            "based on",
            "here is",
            "here are",
            "this is",
            "that is"
        ]
        
        has_good_indicators = any(indicator in response.lower() for indicator in good_indicators)
        if has_good_indicators:
            validation_result["score"] += 10
            validation_result["checks"]["proper_answer"] = True
        else:
            validation_result["checks"]["proper_answer"] = False
        
        return validation_result
    
    def display_response(self, response: str):
        """Display the AI response in a formatted way"""
        print("\n" + "="*60)
        print("AI PORTAL RESPONSE")
        print("="*60)
        print(response)
        print("="*60)
    
    def display_metrics(self):
        """Display session metrics"""
        if self.response_metrics["response_times"]:
            avg_time = sum(self.response_metrics["response_times"]) / len(self.response_metrics["response_times"])
            self.response_metrics["average_response_time"] = avg_time
        
        print("\n" + "="*60)
        print("SESSION METRICS")
        print("="*60)
        print(f"Total queries: {self.response_metrics['total_queries']}")
        print(f"Successful responses: {self.response_metrics['successful_responses']}")
        print(f"Failed responses: {self.response_metrics['failed_responses']}")
        
        if self.response_metrics["total_queries"] > 0:
            success_rate = (self.response_metrics["successful_responses"] / self.response_metrics["total_queries"]) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        if self.response_metrics["response_times"]:
            print(f"Average response time: {self.response_metrics['average_response_time']:.2f}s")
            print(f"Min response time: {min(self.response_metrics['response_times']):.2f}s")
            print(f"Max response time: {max(self.response_metrics['response_times']):.2f}s")
        
        print("="*60)
    
    async def run_test_mode(self):
        """Run automated test mode with predefined questions"""
        print("\n" + "="*60)
        print("AUTOMATED TEST MODE")
        print("="*60)
        print(f"Running {len(self.test_questions)} predefined test questions...")
        
        for i, question in enumerate(self.test_questions, 1):
            print(f"\n[TEST {i}/{len(self.test_questions)}] Testing: '{question}'")
            
            response = await self.submit_question(question)
            
            if response:
                print(f"[✓] Test {i} passed")
                if self.debug_mode:
                    self.display_response(response)
            else:
                print(f"[✗] Test {i} failed")
            
            # Brief pause between tests
            if i < len(self.test_questions):
                await asyncio.sleep(2)
        
        print(f"\n[*] Automated testing completed")
        self.display_metrics()
        return True
    
    async def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up resources...")
        try:
            if self.browser_agent.browser:
                # Don't close the browser - just disconnect
                self.logger.info("Disconnecting from browser (keeping browser open)")
                self.browser_agent.browser = None
                self.browser_agent.page = None
                
            if self.playwright_instance:
                await self.playwright_instance.stop()
                self.logger.info("Playwright instance stopped")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def run_interactive_session(self):
        """Run the interactive query session"""
        mode_str = "Test Mode" if self.test_mode else "Interactive Mode"
        debug_str = " (Debug)" if self.debug_mode else ""
        
        print(f"MCP AI Portal Agent - {mode_str}{debug_str}")
        print("=" * 60)
        
        try:
            # Setup
            if not await self.setup():
                print("[-] Setup failed")
                return False
            
            # Connect to browser
            if not await self.connect_to_browser():
                print("[-] Browser connection failed")
                return False
            
            # Check portal status
            if not await self.check_portal_status():
                print("[-] Portal access failed")
                return False
            
            # Run in test mode or interactive mode
            if self.test_mode:
                return await self.run_test_mode()
            else:
                return await self.run_interactive_mode()
                
        except Exception as e:
            print(f"[-] Unexpected error during session: {e}")
            if self.debug_mode:
                self.logger.exception("Session error details:")
            return False
            
        finally:
            await self.cleanup()
            if self.response_metrics["total_queries"] > 0:
                self.display_metrics()
            print("\n[*] Session ended. Thank you for using the AI Portal Agent!")
    
    async def run_interactive_mode(self):
        """Run interactive mode with user input"""
        while True:
            question = await self.get_user_question()
            
            if question is None:
                break
            
            response = await self.submit_question(question)
            
            if response:
                self.display_response(response)
                
                # Ask if user wants to continue
                print(f"\n[?] Would you like to ask another question? (y/n): ", end="")
                try:
                    continue_choice = input().strip().lower()
                    if continue_choice not in ['y', 'yes', '']:
                        break
                except KeyboardInterrupt:
                    break
            else:
                print("[-] Failed to get response. Please try again.")
                
                # Ask if user wants to retry
                print(f"\n[?] Would you like to try again? (y/n): ", end="")
                try:
                    retry_choice = input().strip().lower()
                    if retry_choice not in ['y', 'yes', '']:
                        break
                except KeyboardInterrupt:
                    break
        
        return True

async def main():
    """Main function to run the interactive test"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP AI Portal Agent Interactive Test")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with detailed logging")
    parser.add_argument("--test", action="store_true", help="Run automated test mode with predefined questions")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--question", type=str, help="Run a single question and exit")
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(debug_mode=args.debug, verbose=args.verbose)
    
    # Create test instance
    test = InteractiveQueryTest(debug_mode=args.debug, test_mode=args.test)
    
    try:
        if args.question:
            # Single question mode
            print(f"MCP AI Portal Agent - Single Question Mode")
            print("=" * 60)
            
            # Setup and connect
            if not await test.setup():
                print("[-] Setup failed")
                return 1
            
            if not await test.connect_to_browser():
                print("[-] Browser connection failed")
                return 1
            
            if not await test.check_portal_status():
                print("[-] Portal access failed")
                return 1
            
            # Submit single question
            response = await test.submit_question(args.question)
            
            if response:
                test.display_response(response)
                await test.cleanup()
                test.display_metrics()
                return 0
            else:
                print("[-] Failed to get response")
                await test.cleanup()
                return 1
        else:
            # Interactive or test mode
            success = await test.run_interactive_session()
            return 0 if success else 1
            
    except KeyboardInterrupt:
        print("\n\n[*] Goodbye!")
        return 0
    except Exception as e:
        print(f"[-] Fatal error: {e}")
        if args.debug:
            logger.exception("Fatal error details:")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)