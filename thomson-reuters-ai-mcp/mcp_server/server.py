import asyncio
import logging
import sys
import os
import json
from typing import List, Dict, Any

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

from mcp_server.browser_agent import BrowserAgent
from mcp_server.exceptions import BrowserConnectionError, OperationTimeoutError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")


class MCPServer(Server):
    """Main MCP server implementation for the AI Portal Agent."""
    def __init__(self, playwright_instance):
        super().__init__(name="thomson-reuters-ai-mcp", version="1.0.0")
        self.browser_agent = BrowserAgent()
        self.playwright_instance = playwright_instance

        # Define tools using the new MCP API
        self._tools = [
            types.Tool(
                name="ask_ai",
                description="Send a question to the AI portal and return the response",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The question to ask the AI"
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="check_portal_status",
                description="Check the status of the portal connection and authentication",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="list_available_models",
                description="List available AI models in the portal",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="get_portal_session",
                description="Get current portal session information",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            )
        ]

        # Register tool handlers using decorators
        self._register_handlers()

    def _register_handlers(self):
        """Register all tool handlers using the new decorator pattern"""

        @self.call_tool()
        async def handle_tools(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle all tool calls"""
            logger.info("Tool called: %s with arguments: %s", name, arguments)

            try:
                if name == "ask_ai":
                    return await self._handle_ask_ai(arguments)
                if name == "check_portal_status":
                    return await self._handle_check_portal_status(arguments)
                if name == "list_available_models":
                    return await self._handle_list_available_models(arguments)
                if name == "get_portal_session":
                    return await self._handle_get_portal_session(arguments)
                return [types.TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'"
                )]
            except Exception as e:
                logger.error("Error in tool %s: %s", name, e)
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def list_tools(self) -> List[types.Tool]:
        """Return the list of available tools"""
        return self._tools

    async def _handle_ask_ai(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle ask_ai tool call"""
        query = arguments.get("query")
        if not query:
            return [types.TextContent(type="text", text="Error: 'query' parameter is required")]

        logger.info("ask_ai called with query: %s", query)
        try:
            response_text = await self.browser_agent.ask_ai(query)
            logger.info("AI response received: %s...", response_text[:100])
            return [types.TextContent(type="text", text=response_text)]
        except Exception as e:
            logger.error("Error in ask_ai: %s", e)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_check_portal_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle check_portal_status tool call"""
        logger.info("check_portal_status called")
        try:
            status = await self.browser_agent.check_portal_status()
            status_text = json.dumps(status, indent=2)
            return [types.TextContent(type="text", text=status_text)]
        except Exception as e:
            logger.error("Error in check_portal_status: %s", e)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_list_available_models(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list_available_models tool call"""
        logger.info("list_available_models called")
        try:
            models = await self.browser_agent.list_available_models()
            models_text = json.dumps(models, indent=2)
            return [types.TextContent(type="text", text=models_text)]
        except Exception as e:
            logger.error("Error in list_available_models: %s", e)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def _handle_get_portal_session(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get_portal_session tool call"""
        logger.info("get_portal_session called")
        try:
            session = await self.browser_agent.get_portal_session()
            session_text = json.dumps(session, indent=2)
            return [types.TextContent(type="text", text=session_text)]
        except Exception as e:
            logger.error("Error in get_portal_session: %s", e)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def start(self):
        """Start the MCP server and connect to browser"""
        try:
            await self.browser_agent.connect_to_browser(self.playwright_instance)
            logger.info("MCP Server started and browser connected successfully")
        except BrowserConnectionError as e:
            logger.error("Failed to start MCP server: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected error starting MCP server: %s", e)
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
            logger.error("Error stopping MCP server: %s", e)
            raise


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
            logger.error("Server error: %s", e)
            raise
        finally:
            await server.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)
