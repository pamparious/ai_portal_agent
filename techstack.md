# Technical Stack

## Core Technologies

### Python 3.9+
- Primary language for MCP server implementation
- Async support for concurrent operations
- Strong ecosystem for automation tools

### Playwright
- Browser automation framework
- CDP (Chrome DevTools Protocol) support for connecting to existing sessions
- Reliable element selection and interaction
- Built-in wait strategies

### MCP (Model Context Protocol)
- Standardized protocol for AI tool integration
- JSON-RPC based communication
- Tool definition and discovery

### Microsoft Edge
- Target browser (Chromium-based)
- Existing profile with SSO sessions
- Developer tools access via CDP

## Key Libraries

```python
playwright==1.40.0          # Browser automation
mcp==0.1.0                 # MCP server implementation  
python-dotenv==1.0.0       # Environment configuration
asyncio                    # Async programming (built-in)
logging                    # Error tracking (built-in)
json                       # Data serialization (built-in)