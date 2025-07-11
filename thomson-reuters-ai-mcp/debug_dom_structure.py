#!/usr/bin/env python3
"""
Debug script to analyze DOM structure and find correct selectors
"""

import asyncio
import logging
from mcp_server.browser_agent import BrowserAgent
from src.portal.portal_interface import PortalInterface
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_dom_structure():
    """Debug the DOM structure to find correct selectors"""
    
    agent = BrowserAgent()
    playwright_instance = None
    
    try:
        playwright_instance = await async_playwright().start()
        await agent.connect_to_browser(playwright_instance)
        
        page = agent.page
        portal = PortalInterface(page)
        
        print("=== DOM STRUCTURE DEBUG ===")
        
        # 1. Get all elements with text content
        print("\n1. FINDING ALL ELEMENTS WITH SUBSTANTIAL TEXT:")
        try:
            # Get all divs with text content
            all_divs = page.locator('div')
            div_count = await all_divs.count()
            print(f"Total divs found: {div_count}")
            
            # Analyze first 20 divs with text
            text_elements = []
            for i in range(min(div_count, 50)):
                try:
                    div = all_divs.nth(i)
                    text = await div.inner_text()
                    if text and len(text.strip()) > 20:
                        # Get element attributes
                        class_name = await div.get_attribute('class')
                        data_attrs = await div.evaluate('el => Object.fromEntries(Array.from(el.attributes).filter(attr => attr.name.startsWith("data-")).map(attr => [attr.name, attr.value]))')
                        
                        text_elements.append({
                            'index': i,
                            'text': text[:100],
                            'class': class_name,
                            'data': data_attrs
                        })
                        
                except Exception as e:
                    continue
            
            print(f"\nFound {len(text_elements)} elements with substantial text:")
            for elem in text_elements:
                print(f"  Element {elem['index']}:")
                print(f"    Class: {elem['class']}")
                print(f"    Data: {elem['data']}")
                print(f"    Text: {elem['text']}...")
                print()
                
        except Exception as e:
            print(f"Error analyzing divs: {e}")
        
        # 2. Look for specific patterns
        print("\n2. LOOKING FOR SPECIFIC PATTERNS:")
        patterns = [
            'Andreas Pils',
            'Claude 4 Sonnet',
            'The capital of Germany',
            'Berlin',
            'just now',
            '3m ago',
            'AI',
            'AP',
        ]
        
        for pattern in patterns:
            try:
                elements = page.locator(f'*:has-text("{pattern}")')
                count = await elements.count()
                print(f"  Pattern '{pattern}': {count} elements found")
                
                if count > 0 and count < 10:  # Analyze if reasonable number
                    for i in range(count):
                        element = elements.nth(i)
                        tag = await element.evaluate('el => el.tagName')
                        class_name = await element.get_attribute('class')
                        text = await element.inner_text()
                        print(f"    Element {i}: <{tag}> class='{class_name}'")
                        print(f"      Text: {text[:80]}...")
                        
            except Exception as e:
                print(f"  Error with pattern '{pattern}': {e}")
        
        # 3. Analyze conversation structure
        print("\n3. ANALYZING CONVERSATION STRUCTURE:")
        try:
            # Look for conversation-like patterns
            conversation_patterns = [
                'div:has-text("Andreas Pils")',
                'div:has-text("Claude 4 Sonnet")',
                'div:has-text("What is the capital")',
                'div:has-text("The capital of Germany")',
                'div:has-text("Berlin")',
            ]
            
            for pattern in conversation_patterns:
                try:
                    elements = page.locator(pattern)
                    count = await elements.count()
                    print(f"  Pattern '{pattern}': {count} elements")
                    
                    if count > 0:
                        for i in range(min(count, 3)):
                            element = elements.nth(i)
                            text = await element.inner_text()
                            position = await element.bounding_box()
                            print(f"    Element {i}: y={position['y'] if position else 'unknown'}")
                            print(f"      Text: {text[:100]}...")
                            
                except Exception as e:
                    print(f"  Error with pattern '{pattern}': {e}")
                    
        except Exception as e:
            print(f"Error in conversation analysis: {e}")
        
        # 4. Get page HTML structure (limited)
        print("\n4. HTML STRUCTURE SAMPLE:")
        try:
            # Get a sample of the HTML structure
            body_html = await page.inner_html('body')
            # Look for conversation-related HTML
            lines = body_html.split('\n')
            conversation_lines = []
            for line in lines:
                if any(keyword in line.lower() for keyword in ['andreas', 'claude', 'capital', 'germany', 'berlin']):
                    conversation_lines.append(line.strip())
            
            print("  Conversation-related HTML:")
            for line in conversation_lines[:10]:  # First 10 relevant lines
                print(f"    {line}")
                
        except Exception as e:
            print(f"Error getting HTML structure: {e}")
        
        # 5. Take screenshot for visual reference
        await portal.take_screenshot("debug_dom_structure.png")
        
        print("\n=== DEBUG COMPLETE ===")
        print("Check debug_dom_structure.png for visual reference")
        
    except Exception as e:
        logger.error(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if agent:
            await agent.close()
        if playwright_instance:
            await playwright_instance.stop()

if __name__ == "__main__":
    asyncio.run(debug_dom_structure())