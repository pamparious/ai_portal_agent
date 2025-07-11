#!/usr/bin/env python3
"""
Terminal interface for MCP AI Portal Agent
Provides command-line interface for VS Code terminal integration
"""

import asyncio
import logging
import sys
import os
from typing import Optional
import click
from datetime import datetime

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server.browser_agent import BrowserAgent
from mcp_server.exceptions import BrowserConnectionError, PortalError, AuthenticationError
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("terminal_interface")


class TerminalInterface:
    """Terminal interface for MCP AI Portal Agent"""
    
    def __init__(self):
        self.browser_agent: Optional[BrowserAgent] = None
        self.playwright_instance = None
        
    async def initialize(self):
        """Initialize the browser connection"""
        try:
            click.echo("🔄 Initializing MCP AI Portal Agent...")
            self.playwright_instance = await async_playwright().start()
            self.browser_agent = BrowserAgent()
            await self.browser_agent.connect_to_browser(self.playwright_instance)
            click.echo("✅ Connected to Edge browser successfully")
            return True
        except BrowserConnectionError as e:
            click.echo(f"❌ Browser connection failed: {e}", err=True)
            return False
        except Exception as e:
            click.echo(f"❌ Initialization failed: {e}", err=True)
            return False
    
    async def cleanup(self):
        """Clean up resources"""
        if self.browser_agent:
            await self.browser_agent.close()
        if self.playwright_instance:
            await self.playwright_instance.stop()
    
    async def ask_ai(self, query: str) -> str:
        """Send query to AI portal and return response"""
        if not self.browser_agent:
            raise RuntimeError("Browser agent not initialized")
        
        try:
            click.echo(f"🤖 Sending query to AI portal...")
            response = await self.browser_agent.ask_ai(query)
            return response
        except AuthenticationError as e:
            click.echo(f"❌ Authentication error: {e}", err=True)
            raise
        except PortalError as e:
            click.echo(f"❌ Portal error: {e}", err=True)
            raise
        except Exception as e:
            click.echo(f"❌ Query failed: {e}", err=True)
            raise
    
    async def check_status(self) -> dict:
        """Check portal status and connection health"""
        if not self.browser_agent:
            raise RuntimeError("Browser agent not initialized")
        
        try:
            status = await self.browser_agent.check_portal_status()
            return status
        except Exception as e:
            click.echo(f"❌ Status check failed: {e}", err=True)
            raise
    
    async def list_models(self) -> list:
        """List available AI models"""
        if not self.browser_agent:
            raise RuntimeError("Browser agent not initialized")
        
        try:
            models = await self.browser_agent.list_available_models()
            return models
        except Exception as e:
            click.echo(f"❌ Model listing failed: {e}", err=True)
            raise


# CLI Commands
@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, verbose):
    """MCP AI Portal Agent - Terminal Interface"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument('query', required=True)
@click.pass_context
def ask(ctx, query):
    """Send a query to the AI portal"""
    async def run_query():
        terminal = TerminalInterface()
        try:
            if await terminal.initialize():
                response = await terminal.ask_ai(query)
                click.echo(f"\n📝 Response:\n{response}")
            else:
                sys.exit(1)
        except KeyboardInterrupt:
            click.echo("\n⏹️  Operation cancelled by user")
            sys.exit(130)
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            sys.exit(1)
        finally:
            await terminal.cleanup()
    
    try:
        asyncio.run(run_query())
    except KeyboardInterrupt:
        click.echo("\n⏹️  Operation cancelled by user")
        sys.exit(130)


@cli.command()
@click.pass_context
def status(ctx):
    """Check portal status and connection health"""
    async def check_status():
        terminal = TerminalInterface()
        try:
            if await terminal.initialize():
                status = await terminal.check_status()
                click.echo("\n📊 Portal Status:")
                click.echo(f"✓ Browser connection: {status.get('browser_connected', 'Unknown')}")
                click.echo(f"✓ Portal authentication: {status.get('authenticated', 'Unknown')}")
                click.echo(f"✓ Available models: {', '.join(status.get('available_models', []))}")
                click.echo(f"✓ Session status: {status.get('session_status', 'Unknown')}")
            else:
                sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Status check failed: {e}", err=True)
            sys.exit(1)
        finally:
            await terminal.cleanup()
    
    try:
        asyncio.run(check_status())
    except KeyboardInterrupt:
        click.echo("\n⏹️  Operation cancelled by user")
        sys.exit(130)


@cli.command()
@click.pass_context
def models(ctx):
    """List available AI models"""
    async def list_models():
        terminal = TerminalInterface()
        try:
            if await terminal.initialize():
                models = await terminal.list_models()
                click.echo("\n🤖 Available AI Models:")
                for model in models:
                    click.echo(f"  • {model}")
            else:
                sys.exit(1)
        except Exception as e:
            click.echo(f"❌ Model listing failed: {e}", err=True)
            sys.exit(1)
        finally:
            await terminal.cleanup()
    
    try:
        asyncio.run(list_models())
    except KeyboardInterrupt:
        click.echo("\n⏹️  Operation cancelled by user")
        sys.exit(130)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Start interactive mode for continuous queries"""
    async def run_interactive():
        terminal = TerminalInterface()
        try:
            if not await terminal.initialize():
                sys.exit(1)
            
            click.echo("\n🚀 Interactive Mode - MCP AI Portal Agent")
            click.echo("Type 'quit' or 'exit' to end session, 'help' for commands")
            click.echo("-" * 50)
            
            while True:
                try:
                    query = click.prompt("\n💬 Ask AI", type=str)
                    
                    if query.lower() in ['quit', 'exit']:
                        click.echo("👋 Goodbye!")
                        break
                    elif query.lower() == 'help':
                        click.echo("\nAvailable commands:")
                        click.echo("  • Type any question to ask the AI")
                        click.echo("  • 'status' - Check portal status")
                        click.echo("  • 'models' - List available models")
                        click.echo("  • 'quit' or 'exit' - End session")
                        continue
                    elif query.lower() == 'status':
                        status = await terminal.check_status()
                        click.echo(f"\n📊 Status: {status}")
                        continue
                    elif query.lower() == 'models':
                        models = await terminal.list_models()
                        click.echo(f"\n🤖 Models: {', '.join(models)}")
                        continue
                    
                    if query.strip():
                        response = await terminal.ask_ai(query)
                        click.echo(f"\n📝 Response:\n{response}")
                    
                except KeyboardInterrupt:
                    click.echo("\n⏹️  Use 'quit' or 'exit' to end session")
                    continue
                except EOFError:
                    click.echo("\n👋 Goodbye!")
                    break
                except Exception as e:
                    click.echo(f"❌ Error: {e}", err=True)
                    continue
        
        except KeyboardInterrupt:
            click.echo("\n⏹️  Session ended by user")
        finally:
            await terminal.cleanup()
    
    try:
        asyncio.run(run_interactive())
    except KeyboardInterrupt:
        click.echo("\n👋 Goodbye!")
        sys.exit(130)


if __name__ == '__main__':
    cli()