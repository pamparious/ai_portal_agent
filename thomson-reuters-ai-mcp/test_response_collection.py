#!/usr/bin/env python3
"""
Test script to verify improved response collection logic.
"""

import asyncio
import logging
from mcp_server.browser_agent import BrowserAgent
from src.portal.portal_interface import PortalInterface
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_response_collection():
    """Test the improved response collection logic"""
    
    agent = BrowserAgent()
    playwright_instance = None
    
    try:
        playwright_instance = await async_playwright().start()
        await agent.connect_to_browser(playwright_instance)
        
        page = agent.page
        portal = PortalInterface(page)
        
        # Take initial screenshot
        await portal.take_screenshot("test_before_response.png")
        
        print("=== TESTING RESPONSE COLLECTION ===")
        
        # Test the message analysis methods
        print("\n1. Getting ordered messages...")
        messages = await portal._get_ordered_messages()
        print(f"Found {len(messages)} messages:")
        
        for i, msg in enumerate(messages):
            print(f"  Message {i+1}: type={msg['type']}, position={msg['position']}")
            print(f"    Text: {msg['text'][:80]}..." if len(msg['text']) > 80 else f"    Text: {msg['text']}")
            print()
        
        # Test response extraction
        print("\n2. Testing response extraction...")
        response = await portal._get_latest_response()
        if response:
            print(f"✓ Successfully extracted response: {response}")
        else:
            print("✗ No response found")
        
        # Test text cleaning
        print("\n3. Testing text cleaning...")
        if messages:
            for msg in messages:
                if msg['type'] == 'ai':
                    cleaned = portal._clean_ai_response_text(msg['text'])
                    print(f"Original: {msg['text']}")
                    print(f"Cleaned:  {cleaned}")
                    print()
        
        # Test user message detection
        print("\n4. Testing user message detection...")
        if messages:
            for msg in messages:
                is_user = portal._is_user_message(msg['text'])
                print(f"Text: {msg['text'][:50]}...")
                print(f"Detected as user message: {is_user}")
                print()
        
        # Test sending a new message and getting response
        print("\n5. Testing full workflow...")
        test_question = "What is the capital of Germany?"
        
        try:
            print(f"Sending question: {test_question}")
            await portal.send_message(test_question)
            
            print("Waiting for response...")
            response = await portal.wait_for_response(timeout=30)
            print(f"✓ Received response: {response}")
            
        except Exception as e:
            print(f"✗ Error in full workflow test: {e}")
        
        # Take final screenshot
        await portal.take_screenshot("test_after_response.png")
        
        print("\n=== TEST COMPLETE ===")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if agent:
            await agent.close()
        if playwright_instance:
            await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(test_response_collection())