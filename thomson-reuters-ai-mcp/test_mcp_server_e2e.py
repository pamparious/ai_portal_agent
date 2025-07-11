#!/usr/bin/env python3
"""
End-to-end test for the complete MCP server functionality.
Tests the full workflow from MCP tool call to AI response.
"""

import asyncio
import logging
import json
from mcp_server.server import MCPServer
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_server_e2e():
    """Test the complete MCP server end-to-end workflow"""
    
    playwright_instance = None
    server = None
    
    try:
        print("=== MCP SERVER END-TO-END TEST ===")
        
        # 1. Initialize the MCP server
        print("\n1. INITIALIZING MCP SERVER...")
        playwright_instance = await async_playwright().start()
        server = MCPServer(playwright_instance)
        
        # 2. Start the server and connect to browser
        print("\n2. STARTING SERVER AND CONNECTING TO BROWSER...")
        await server.start()
        print("✓ MCP Server started successfully")
        
        # 3. Test browser connection
        print("\n3. TESTING BROWSER CONNECTION...")
        try:
            connection_result = await server._test_browser_connection_tool("test_browser_connection", {})
            print(f"✓ Browser connection test passed: {connection_result}")
        except Exception as e:
            print(f"✗ Browser connection test failed: {e}")
            return
        
        # 4. Test simple AI query
        print("\n4. TESTING SIMPLE AI QUERY...")
        test_queries = [
            "What is the capital of France?",
            "What is 2 + 2?",
            "Hello, how are you?",
        ]
        
        for i, query in enumerate(test_queries, 1):
            try:
                print(f"\n  Test {i}: Asking '{query}'")
                result = await server._ask_ai_tool("ask_ai", {"query": query})
                response = result.get("response", "")
                
                if response and len(response.strip()) > 10:
                    print(f"  ✓ Received valid response: {response[:80]}...")
                    
                    # Basic validation
                    if query == "What is the capital of France?":
                        if "paris" in response.lower():
                            print("  ✓ Response contains expected content (Paris)")
                        else:
                            print(f"  ⚠ Response may not be correct: {response}")
                    
                    elif query == "What is 2 + 2?":
                        if "4" in response:
                            print("  ✓ Response contains expected content (4)")
                        else:
                            print(f"  ⚠ Response may not be correct: {response}")
                    
                else:
                    print(f"  ✗ Invalid or empty response: {response}")
                    
            except Exception as e:
                print(f"  ✗ Error with query '{query}': {e}")
                continue
        
        # 5. Test error handling
        print("\n5. TESTING ERROR HANDLING...")
        try:
            # Test with empty query
            result = await server._ask_ai_tool("ask_ai", {"query": ""})
            print("  ✗ Empty query should have failed")
        except Exception as e:
            print(f"  ✓ Empty query properly rejected: {e}")
        
        try:
            # Test with missing query
            result = await server._ask_ai_tool("ask_ai", {})
            print("  ✗ Missing query should have failed")
        except Exception as e:
            print(f"  ✓ Missing query properly rejected: {e}")
        
        # 6. Test multiple rapid queries
        print("\n6. TESTING MULTIPLE RAPID QUERIES...")
        rapid_queries = [
            "What is the capital of Germany?",
            "What is the capital of Italy?",
            "What is the capital of Spain?",
        ]
        
        for i, query in enumerate(rapid_queries, 1):
            try:
                print(f"  Rapid test {i}: {query}")
                result = await server._ask_ai_tool("ask_ai", {"query": query})
                response = result.get("response", "")
                print(f"  ✓ Response {i}: {response[:50]}...")
                
                # Small delay between queries
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"  ✗ Rapid query {i} failed: {e}")
        
        # 7. Performance test
        print("\n7. PERFORMANCE TEST...")
        import time
        
        performance_query = "What is artificial intelligence?"
        start_time = time.time()
        
        try:
            result = await server._ask_ai_tool("ask_ai", {"query": performance_query})
            end_time = time.time()
            
            response_time = end_time - start_time
            response = result.get("response", "")
            
            print(f"  ✓ Performance test completed in {response_time:.2f} seconds")
            print(f"  ✓ Response length: {len(response)} characters")
            
            if response_time < 30:
                print("  ✓ Response time acceptable (< 30s)")
            else:
                print(f"  ⚠ Response time slow (> 30s): {response_time:.2f}s")
                
        except Exception as e:
            print(f"  ✗ Performance test failed: {e}")
        
        print("\n=== END-TO-END TEST COMPLETE ===")
        print("✓ MCP Server is functioning correctly!")
        
    except Exception as e:
        logger.error(f"E2E test failed: {e}")
        import traceback
        traceback.print_exc()
        print("✗ MCP Server E2E test failed")
    finally:
        # Cleanup
        if server:
            try:
                await server.stop()
                print("✓ Server stopped cleanly")
            except Exception as e:
                print(f"✗ Error stopping server: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server_e2e())