# MCP AI Portal Agent

A Python-based MCP (Model Context Protocol) server that enables secure access to Thomson Reuters' AI portal through browser automation.

## Features

- **Secure Browser Connection**: Connects to existing Edge or Chrome browser sessions without storing credentials
- **MCP Protocol Support**: Full MCP server implementation with 4 core tools
- **CLI Interface**: Command-line interface for VS Code terminal integration
- **Robust Portal Integration**: Dynamic DOM selectors and retry logic
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Custom exception classes and comprehensive logging

## Installation

1. **Prerequisites**:
   - Python 3.8+
   - Microsoft Edge or Google Chrome browser
   - Node.js (for Playwright)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Configure your browser**:
   Start your browser with debugging enabled (preserves your login data):
   
   **Option A: Use the provided scripts (Recommended)**
   
   For Microsoft Edge:
   ```bash
   # Windows Command Prompt
   start-edge-debug.bat
   
   # PowerShell
   .\start-edge-debug.ps1
   ```
   
   For Google Chrome:
   ```bash
   # Windows Command Prompt
   start-chrome-debug.bat
   
   # PowerShell
   .\start-chrome-debug.ps1
   ```
   
   **Option B: Manual command (preserves existing profile)**
   
   For Microsoft Edge:
   ```bash
   # Windows Command Prompt
   "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
   
   # PowerShell
   & "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
   
   # Alternative location (newer installs)
   "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
   ```
   
   For Google Chrome:
   ```bash
   # Windows Command Prompt
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   
   # PowerShell
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   
   # Alternative location (32-bit installs)
   "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   ```
   
   **⚠️ Important**: Do NOT use `--user-data-dir` parameter as this would create a new profile without your Thomson Reuters login data.

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

- **No Credential Storage**: Uses existing browser sessions and login data
- **Profile Preservation**: Uses default browser profile to maintain Thomson Reuters authentication
- **Input Validation**: Sanitizes all inputs and responses
- **Domain Restrictions**: Configured allowed domains
- **Audit Logging**: Comprehensive logging for compliance
- **Session Management**: Automatically detects and uses existing login sessions

## Troubleshooting

### Common Issues

1. **Browser Connection Failed**:
   - Ensure your browser (Edge or Chrome) is running with the correct command (see installation section)
   - Check firewall settings - port 9222 must be accessible
   - Verify port 9222 is not in use by another application
   - Try different browser installation paths if needed

2. **Authentication Required**:
   - Ensure you're using the default browser profile (no `--user-data-dir` parameter)
   - Log in to Thomson Reuters portal manually in your regular browser
   - Verify session is active before starting the agent
   - If using helper scripts, they automatically preserve your login data

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