#!/usr/bin/env python3
"""
Debug script to scrape and analyze the AI chat interface structure.
This helps identify how to distinguish user messages from AI responses.
"""

import asyncio
import logging
import json
from playwright.async_api import async_playwright
from mcp_server.browser_agent import BrowserAgent
from src.portal.portal_interface import PortalInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analyze_chat_interface():
    """Analyze the chat interface structure to understand message patterns"""
    
    agent = BrowserAgent()
    playwright_instance = None
    
    try:
        playwright_instance = await async_playwright().start()
        await agent.connect_to_browser(playwright_instance)
        
        page = agent.page
        portal = PortalInterface(page)
        
        # Take initial screenshot
        await portal.take_screenshot("debug_before_analysis.png")
        
        print("=== ANALYZING CHAT INTERFACE ===")
        
        # 1. Get all message-related elements
        print("\n1. SCANNING FOR MESSAGE ELEMENTS:")
        message_selectors = [
            '[data-testid*="message"]',
            '[class*="message"]',
            '[role="article"]',
            'div[class*="chat"]',
            'div[class*="conversation"]',
            'div[class*="bubble"]',
            'div[data-role*="message"]',
            'div[data-type*="message"]',
            '.user-message',
            '.ai-message',
            '.assistant-message',
            '.human-message',
        ]
        
        for selector in message_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                if count > 0:
                    print(f"  ✓ Found {count} elements with selector: {selector}")
                    
                    # Get details about each element
                    for i in range(min(count, 3)):  # Limit to first 3 for analysis
                        element = elements.nth(i)
                        text = await element.inner_text()
                        class_name = await element.get_attribute('class')
                        data_attrs = await element.evaluate('el => Object.fromEntries(Array.from(el.attributes).filter(attr => attr.name.startsWith("data-")).map(attr => [attr.name, attr.value]))')
                        
                        print(f"    Element {i}: class='{class_name}', data={data_attrs}")
                        print(f"    Text: {text[:100]}..." if len(text) > 100 else f"    Text: {text}")
                        print()
                        
            except Exception as e:
                print(f"  ✗ Error with selector {selector}: {e}")
        
        # 2. Analyze conversation structure
        print("\n2. ANALYZING CONVERSATION STRUCTURE:")
        
        # Look for conversation containers
        conversation_selectors = [
            '[class*="conversation"]',
            '[class*="chat"]',
            '[class*="messages"]',
            '[role="log"]',
            '[role="main"]',
            'main',
            '.chat-container',
            '.conversation-container',
        ]
        
        for selector in conversation_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                if count > 0:
                    print(f"  ✓ Found {count} conversation containers with: {selector}")
                    
                    # Get the HTML structure
                    container = elements.first
                    html = await container.inner_html()
                    print(f"    HTML structure preview: {html[:200]}...")
                    
            except Exception as e:
                print(f"  ✗ Error with selector {selector}: {e}")
        
        # 3. Look for specific message patterns
        print("\n3. LOOKING FOR MESSAGE PATTERNS:")
        
        # Get all text content
        body_text = await page.inner_text('body')
        
        # Look for common chat patterns
        patterns = [
            'user:',
            'assistant:',
            'human:',
            'ai:',
            'you:',
            'me:',
            'User Message',
            'AI Response',
            'Assistant Response',
        ]
        
        for pattern in patterns:
            if pattern.lower() in body_text.lower():
                print(f"  ✓ Found pattern: '{pattern}'")
        
        # 4. Check for timestamp or order indicators
        print("\n4. CHECKING FOR ORDER INDICATORS:")
        
        timestamp_selectors = [
            '[data-timestamp]',
            '[class*="timestamp"]',
            '[class*="time"]',
            '.message-time',
            '.chat-time',
            'time',
            '[datetime]',
        ]
        
        for selector in timestamp_selectors:
            try:
                elements = page.locator(selector)
                count = await elements.count()
                if count > 0:
                    print(f"  ✓ Found {count} timestamp elements with: {selector}")
                    
                    # Get sample timestamps
                    for i in range(min(count, 3)):
                        element = elements.nth(i)
                        text = await element.inner_text()
                        datetime_attr = await element.get_attribute('datetime')
                        print(f"    Timestamp {i}: text='{text}', datetime='{datetime_attr}'")
                        
            except Exception as e:
                print(f"  ✗ Error with selector {selector}: {e}")
        
        # 5. Look for message ordering/threading
        print("\n5. ANALYZING MESSAGE ORDERING:")
        
        # Check for parent-child relationships
        try:
            # Get all potential message containers
            all_messages = page.locator('div').filter(has_text=lambda text: len(text) > 10)
            count = await all_messages.count()
            
            print(f"  Found {count} div elements with substantial text")
            
            # Analyze the last few messages to understand structure
            for i in range(max(0, count-5), count):
                try:
                    element = all_messages.nth(i)
                    text = await element.inner_text()
                    if len(text) > 20:  # Skip very short texts
                        position = await element.bounding_box()
                        print(f"    Message {i}: position_y={position['y'] if position else 'unknown'}")
                        print(f"      Text: {text[:80]}..." if len(text) > 80 else f"      Text: {text}")
                        
                except Exception as e:
                    print(f"    Error analyzing message {i}: {e}")
                    
        except Exception as e:
            print(f"  Error analyzing message ordering: {e}")
        
        # 6. Take final screenshot
        await portal.take_screenshot("debug_after_analysis.png")
        
        print("\n=== ANALYSIS COMPLETE ===")
        print("Check debug_before_analysis.png and debug_after_analysis.png for visual reference")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise
    finally:
        if agent:
            await agent.close()
        if playwright_instance:
            await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(analyze_chat_interface())