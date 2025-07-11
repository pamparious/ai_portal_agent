#!/usr/bin/env python3
"""
Simple test to verify MCP tools are working correctly
"""

import asyncio
import json
import logging
from mcp_server.server import MCPServer
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_tools():
    """Test individual MCP tools"""
    
    playwright_instance = None
    server = None
    
    try:
        print("=== MCP TOOLS TEST ===")
        
        # Initialize and start server
        playwright_instance = await async_playwright().start()
        server = MCPServer(playwright_instance)
        await server.start()
        
        print("✓ MCP Server initialized")
        
        # Test 1: Browser connection tool
        print("\n1. Testing browser connection tool...")
        try:
            result = await server._test_browser_connection_tool("test_browser_connection", {})
            print(f"✓ Browser connection successful")
            print(f"  Page title: {result.get('page_title', 'Unknown')}")
        except Exception as e:
            print(f"✗ Browser connection failed: {e}")
            return
        
        # Test 2: AI query tool
        print("\n2. Testing AI query tool...")
        test_query = "What is the capital of France?"
        
        try:
            result = await server._ask_ai_tool("ask_ai", {"query": test_query})
            response = result.get("response", "")
            
            print(f"✓ AI query successful")
            print(f"  Query: {test_query}")
            print(f"  Response: {response}")
            
            # Validate response
            if response and len(response.strip()) > 5:
                if "paris" in response.lower():
                    print("✓ Response validation passed")
                else:
                    print("⚠ Response may not be accurate")
            else:
                print("✗ Response validation failed - empty or too short")
                
        except Exception as e:
            print(f"✗ AI query failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Another query to confirm consistency
        print("\n3. Testing second AI query...")
        test_query2 = "What is 5 + 3?"
        
        try:
            result = await server._ask_ai_tool("ask_ai", {"query": test_query2})
            response = result.get("response", "")
            
            print(f"✓ Second AI query successful")
            print(f"  Query: {test_query2}")
            print(f"  Response: {response}")
            
            # Validate response
            if "8" in response:
                print("✓ Mathematical response validation passed")
            else:
                print("⚠ Mathematical response may not be accurate")
                
        except Exception as e:
            print(f"✗ Second AI query failed: {e}")
        
        print("\n=== MCP TOOLS TEST COMPLETE ===")
        
    except Exception as e:
        logger.error(f"MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if server:
            await server.stop()

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())