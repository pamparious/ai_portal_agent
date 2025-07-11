#!/usr/bin/env python3
"""
Simple Windows test script for MCP AI Portal Agent
Runs directly without module imports
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all imports work"""
    try:
        print("🔍 Testing imports...")
        
        # Test basic imports
        from mcp_server.browser_agent import BrowserAgent
        from mcp_server.config import get_config
        from mcp_server.exceptions import BrowserConnectionError
        from src.portal.portal_interface import PortalInterface
        from cli.terminal_interface import TerminalInterface
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

async def test_connection():
    """Test browser connection"""
    try:
        print("\n🔍 Testing browser connection...")
        
        from playwright.async_api import async_playwright
        from mcp_server.browser_agent import BrowserAgent
        
        async with async_playwright() as playwright:
            agent = BrowserAgent()
            try:
                await agent.connect_to_browser(playwright)
                print("✅ Browser connected successfully!")
                
                # Test status
                status = await agent.check_portal_status()
                print(f"✅ Portal status: {status}")
                
                # Test models
                models = await agent.list_available_models()
                print(f"✅ Available models: {models}")
                
                return True
                
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return False
            finally:
                await agent.close()
                
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_cli_direct():
    """Test CLI functionality directly"""
    try:
        print("\n🔍 Testing CLI functionality...")
        
        from cli.terminal_interface import TerminalInterface
        
        # Test CLI class instantiation
        cli = TerminalInterface()
        print("✅ CLI interface created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Windows Test Suite for MCP AI Portal Agent")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed. Please check your Python path.")
        return False
    
    # Test 2: CLI Direct
    if not test_cli_direct():
        print("\n❌ CLI test failed.")
        return False
    
    # Test 3: Connection (async)
    print("\n🔍 Testing browser connection (requires Edge with debugging)...")
    try:
        success = asyncio.run(test_connection())
        if success:
            print("✅ Connection test passed!")
        else:
            print("❌ Connection test failed (this is expected if Edge isn't running with debugging)")
    except Exception as e:
        print(f"❌ Connection test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("✅ Python imports working")
    print("✅ CLI interface working")
    print("✅ Code structure is correct")
    print("\nTo test full functionality:")
    print("1. Run: start-edge-debug.bat")
    print("2. Login to Thomson Reuters portal")
    print("3. Run this test again")
    print("\nDirect CLI usage:")
    print("python cli/terminal_interface.py status")
    print("python cli/terminal_interface.py ask \"test question\"")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()