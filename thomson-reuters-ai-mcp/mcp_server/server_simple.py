#!/usr/bin/env python3
"""
Simple MCP server implementation for testing
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from playwright.async_api import async_playwright
from mcp_server.browser_agent import BrowserAgent
from mcp_server.exceptions import BrowserConnectionError, PortalError
from mcp_server.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simple_server")


class SimpleMCPServer:
    """Simple MCP server for testing the browser agent"""
    
    def __init__(self):
        self.config = get_config()
        self.browser_agent = BrowserAgent()
        self.playwright_instance = None
    
    async def start(self):
        """Start the server and connect to browser"""
        logger.info("Starting Simple MCP Server...")
        
        try:
            self.playwright_instance = await async_playwright().start()
            await self.browser_agent.connect_to_browser(self.playwright_instance)
            logger.info("Server started successfully")
            return True
        except BrowserConnectionError as e:
            logger.error(f"Browser connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Server startup failed: {e}")
            return False
    
    async def ask_ai(self, query: str) -> str:
        """Ask AI tool"""
        try:
            response = await self.browser_agent.ask_ai(query)
            return response
        except Exception as e:
            logger.error(f"Ask AI failed: {e}")
            raise
    
    async def check_status(self) -> Dict[str, Any]:
        """Check portal status"""
        try:
            status = await self.browser_agent.check_portal_status()
            return status
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            raise
    
    async def list_models(self) -> list:
        """List available models"""
        try:
            models = await self.browser_agent.list_available_models()
            return models
        except Exception as e:
            logger.error(f"List models failed: {e}")
            raise
    
    async def get_session(self) -> Dict[str, Any]:
        """Get session info"""
        try:
            session = await self.browser_agent.get_portal_session()
            return session
        except Exception as e:
            logger.error(f"Get session failed: {e}")
            raise
    
    async def stop(self):
        """Stop the server"""
        logger.info("Stopping server...")
        try:
            if self.browser_agent:
                await self.browser_agent.close()
            if self.playwright_instance:
                await self.playwright_instance.stop()
            logger.info("Server stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping server: {e}")


async def test_server():
    """Test the simple server functionality"""
    server = SimpleMCPServer()
    
    try:
        # Test server startup
        if await server.start():
            logger.info("✅ Server started successfully")
            
            # Test status check
            try:
                status = await server.check_status()
                logger.info(f"✅ Status check: {status}")
            except Exception as e:
                logger.error(f"❌ Status check failed: {e}")
            
            # Test models listing
            try:
                models = await server.list_models()
                logger.info(f"✅ Models list: {models}")
            except Exception as e:
                logger.error(f"❌ Models list failed: {e}")
            
            # Test session info
            try:
                session = await server.get_session()
                logger.info(f"✅ Session info: {session}")
            except Exception as e:
                logger.error(f"❌ Session info failed: {e}")
            
            # Test ask AI (this will likely fail without browser)
            try:
                response = await server.ask_ai("What is the capital of France?")
                logger.info(f"✅ AI response: {response}")
            except Exception as e:
                logger.error(f"❌ AI query failed: {e}")
                
        else:
            logger.error("❌ Server failed to start")
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        
    finally:
        await server.stop()


if __name__ == "__main__":
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)