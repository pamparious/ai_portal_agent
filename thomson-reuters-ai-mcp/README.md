# MCP AI Portal Agent

A Python-based MCP (Model Context Protocol) server that enables secure access to Thomson Reuters' AI portal through browser automation.

## Features

- **Secure Browser Connection**: Connects to existing Edge browser sessions without storing credentials
- **MCP Protocol Support**: Full MCP server implementation with 4 core tools
- **CLI Interface**: Command-line interface for VS Code terminal integration
- **Robust Portal Integration**: Dynamic DOM selectors and retry logic
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Custom exception classes and comprehensive logging

## Installation

1. **Prerequisites**:
   - Python 3.8+
   - Microsoft Edge browser
   - Node.js (for Playwright)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Configure Edge browser**:
   Start Edge with debugging enabled:
   ```bash
   msedge.exe --remote-debugging-port=9222 --user-data-dir=C:\\temp\\edge-debug
   ```

4. **Environment setup**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Usage

### CLI Interface

```bash
# Ask a question
python -m cli.terminal_interface ask "What are the current market trends?"

# Check portal status
python -m cli.terminal_interface status

# List available AI models
python -m cli.terminal_interface models

# Interactive mode
python -m cli.terminal_interface interactive
```

### MCP Server

```bash
# Start MCP server
python -m mcp_server.server
```

### Available MCP Tools

1. **ask_ai**: Send queries to the AI portal
2. **check_portal_status**: Check connection health and authentication
3. **list_available_models**: Get available AI models
4. **get_portal_session**: Get current session information

## Configuration

Configure the agent using environment variables or `.env` file:

```env
# Browser settings
MCP_BROWSER_DEBUG_PORT=9222
MCP_BROWSER_TIMEOUT=30000

# Portal settings
MCP_PORTAL_BASE_URL=https://dataandanalytics.int.thomsonreuters.com
MCP_PORTAL_RESPONSE_TIMEOUT=30

# Security settings
MCP_MAX_QUERY_LENGTH=10000
MCP_ENABLE_INPUT_VALIDATION=true
```

## Architecture

```
thomson-reuters-ai-mcp/
├── mcp_server/
│   ├── server.py              # MCP protocol implementation
│   ├── browser_agent.py       # Browser automation
│   ├── exceptions.py          # Custom exceptions
│   └── config.py              # Configuration management
├── src/portal/
│   └── portal_interface.py    # Portal interaction
├── cli/
│   └── terminal_interface.py  # CLI interface
└── tests/                     # Test suite
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Debug Mode

```bash
MCP_LOG_LEVEL=DEBUG python -m cli.terminal_interface ask "test question"
```

## Security

- **No Credential Storage**: Uses existing browser sessions
- **Input Validation**: Sanitizes all inputs and responses
- **Domain Restrictions**: Configured allowed domains
- **Audit Logging**: Comprehensive logging for compliance

## Troubleshooting

### Common Issues

1. **Browser Connection Failed**:
   - Ensure Edge is running with `--remote-debugging-port=9222`
   - Check firewall settings
   - Verify port 9222 is not in use

2. **Authentication Required**:
   - Log in to Thomson Reuters portal manually
   - Verify session is active

3. **Portal UI Changed**:
   - DOM selectors may need updates
   - Check debug screenshots for UI changes

4. **Timeout Issues**:
   - Increase `MCP_PORTAL_RESPONSE_TIMEOUT`
   - Check network connectivity

### Debug Features

- **Screenshots**: Automatic screenshots on errors
- **Verbose Logging**: Set `MCP_LOG_LEVEL=DEBUG`
- **Health Checks**: Built-in connection monitoring

## License

Thomson Reuters Internal Use Only

## Support

For issues and questions, contact the Thomson Reuters AI Platform team.