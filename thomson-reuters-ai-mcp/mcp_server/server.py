import asyncio
import importlib.metadata
import logging
import sys
import os

# Add the project root to the Python path if not already present
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import anyio
from playwright.async_api import async_playwright

import mcp.types as types
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.shared.context import RequestContext

from mcp_server.browser_agent import BrowserAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")


class MCPServer(Server):
    def __init__(self, playwright_instance):
        super().__init__(name="mcp", version=importlib.metadata.version("mcp"))
        self.browser_agent = BrowserAgent()
        self.playwright_instance = playwright_instance

        self.add_tool(
            "ask_ai",
            self._ask_ai_tool,
            input_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            output_schema={"type": "object", "properties": {"response": {"type": "string"}}},
        )

        self.add_tool(
            "test_browser_connection",
            self._test_browser_connection_tool,
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object", "properties": {"page_title": {"type": "string"}}},
        )

    async def _test_browser_connection_tool(self, tool_name: str, arguments: dict) -> dict:
        logger.info("test_browser_connection_tool invoked")
        try:
            title = await self.browser_agent.page.title()
            logger.info(f"Successfully retrieved page title: {title}")
            return {"page_title": title}
        except Exception as e:
            logger.error(f"Error in test_browser_connection_tool: {e}")
            raise

    async def _ask_ai_tool(self, tool_name: str, arguments: dict) -> dict:
        query = arguments.get("query")
        if not query:
            raise ValueError("'query' argument is required for 'ask_ai' tool")
        logger.info(f"ask_ai_tool invoked with query: {query}")
        try:
            response_text = await self.browser_agent.ask_ai(query)
            logger.info(f"ask_ai_tool received response: {response_text}")
            return {"response": response_text}
        except Exception as e:
            logger.error(f"Error in ask_ai tool: {e}")
            raise

    async def start(self):
        """Start the MCP server and connect to browser"""
        try:
            await self.browser_agent.connect_to_browser(self.playwright_instance)
            logger.info("MCP Server started and browser connected successfully")
        except BrowserConnectionError as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error starting MCP server: {e}")
            raise

    async def stop(self):
        """Stop the MCP server and clean up resources"""
        logger.info("Stopping MCP server...")
        try:
            if self.browser_agent:
                await self.browser_agent.close()
            if self.playwright_instance:
                await self.playwright_instance.stop()
            logger.info("MCP server stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping MCP server: {e}")
            raise


def main_docstring():
    """Entry point for the MCP server. Ensures graceful shutdown."""
    pass


async def main():
    """Entry point for the MCP server. Ensures graceful shutdown."""
    logger.info("Starting MCP AI Portal Agent server...")
    
    async with async_playwright() as playwright_instance:
        server = MCPServer(playwright_instance)
        try:
            await server.start()
            logger.info("MCP server is ready to accept connections")
            
            async with stdio_server() as (read_stream, write_stream):
                initialization_options = server.create_initialization_options()
                await server.run(read_stream, write_stream, initialization_options)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down gracefully...")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            await server.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)