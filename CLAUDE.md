# MCP AI Portal Agent - Development Instructions

## Project Overview
You are helping to build an MCP (Model Context Protocol) agent that enables secure access to Thomson Reuters' AI portal through browser automation. This agent will connect to a local Edge browser, navigate to the company's AI portal, interact with Claude Sonnet 4, and return responses to the terminal.

## Core Requirements
- **Security First**: Use existing browser sessions, never store credentials
- **Company Policy Compliance**: Respect Thomson Reuters authentication and usage policies
- **Browser Automation**: Connect to existing Edge browser instance without spawning new sessions
- **MCP Protocol**: Implement proper MCP server with defined tools and handlers
- **Terminal Integration**: Provide seamless VS Code terminal interface

## Technical Architecture

### Component Structure
```
ai-portal-agent/
├── thomson-reuters-ai-mcp/
│   ├── mcp_server/
│   │   ├── server.py              # MCP protocol implementation
│   │   ├── browser_agent.py       # Browser connection & control
│   │   ├── exceptions.py          # Custom exception classes
│   │   └── config.py              # Configuration management
│   ├── src/
│   │   └── portal/
│   │       └── portal_interface.py # AI portal interaction
│   ├── cli/
│   │   └── terminal_interface.py   # Command-line interface
│   └── requirements.txt            # Python dependencies
```

### Key Technologies
- **MCP SDK**: mcp Python package for protocol implementation
- **Browser Automation**: playwright for Edge browser control
- **Python**: Full type hints and modern Python features
- **Logging**: Python logging module for structured logging
- **Click**: CLI argument parsing and command handling

## Implementation Guidelines

### 1. Browser Connection Strategy
- **Never spawn new browser instances** - always connect to existing Edge browser
- Use `puppeteer-core.connect()` with debugging port detection
- Implement connection retry logic with exponential backoff
- Maintain session persistence across agent restarts
- Handle browser crashes and reconnection gracefully

### 2. Portal Interaction Pattern
```typescript
// Expected workflow
1. detectExistingBrowser() -> Connect to Edge
2. navigateToPortal() -> Go to AI portal URL
3. verifyAuthentication() -> Check login status
4. selectClaudeModel() -> Choose Claude Sonnet 4
5. sendQuery() -> Submit user question
6. waitForResponse() -> Monitor for completion
7. extractResponse() -> Parse and format result
8. returnToTerminal() -> Output to CLI
```

### 3. MCP Server Implementation
Define these tools in your MCP server:
- `query-ai-portal`: Send question to Claude and return response
- `check-portal-status`: Verify portal accessibility and authentication
- `list-available-models`: Get available AI models from portal
- `get-portal-session`: Return current session information

### 4. Error Handling Requirements
- **Browser Connection Failures**: Provide clear instructions for browser setup
- **Authentication Issues**: Detect and report login problems
- **Portal Changes**: Gracefully handle UI updates with fallback selectors
- **Network Timeouts**: Implement proper timeout handling with user feedback
- **Rate Limiting**: Respect portal usage limits and implement backoff

## Security & Compliance

### Authentication Approach
- **NO credential storage** - rely on existing browser session
- **Session validation** - verify authentication before each request
- **Audit logging** - log all portal interactions for compliance
- **Timeout handling** - gracefully handle session expiration

### Data Protection
- **No data persistence** - don't store queries or responses
- **Secure communication** - use HTTPS for all portal interactions
- **Error message sanitization** - avoid exposing sensitive information
- **Memory cleanup** - clear sensitive data from memory after use

## Development Phases

### Phase 1: Foundation (Current)
- Project structure and dependencies
- Basic TypeScript configuration
- Logging infrastructure
- Git repository setup

### Phase 2: Browser Integration
- Edge browser detection and connection
- Connection health monitoring
- Basic navigation capabilities
- Error handling for browser issues

### Phase 3: Portal Interface
- AI portal navigation and authentication
- DOM scraping for interface elements
- Model selection (Claude Sonnet 4)
- Query submission and response extraction

### Phase 4: MCP Server
- MCP protocol implementation
- Tool definition and handlers
- Request validation and sanitization
- Response formatting and error handling

### Phase 5: Terminal Interface
- CLI command parsing
- Progress indicators and status updates
- Output formatting and display
- VS Code integration

### Phase 6: Testing & Validation
- Unit tests for all components
- Integration tests for full workflow
- Mock services for testing
- Performance and reliability testing

## Code Quality Standards

### TypeScript Requirements
- **Strict mode enabled** - no implicit any types
- **Interface definitions** - proper typing for all data structures
- **Error types** - specific error classes for different failure modes
- **Async/await** - proper promise handling throughout

### Logging Standards
```typescript
// Use structured logging with Winston
logger.info('Portal query initiated', {
  queryId: uuid(),
  timestamp: new Date().toISOString(),
  userAgent: 'mcp-ai-portal-agent',
  portalUrl: sanitizeUrl(url)
});
```

### Testing Requirements
- **Unit tests** for each component (>90% coverage)
- **Integration tests** for full workflow
- **Mock browser** for testing without real browser
- **Error scenario testing** for all failure modes

## Environment Setup

### Prerequisites
- Windows 11 with Edge or Chrome browser
- Node.js 18+ with npm
- VS Code with TypeScript extension
- Browser with debugging enabled (Edge or Chrome)

### Browser Configuration
Your browser (Edge or Chrome) must be started with debugging enabled (preserves login data):

**Microsoft Edge:**
```bash
# Windows Command Prompt
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222

# PowerShell
& "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222

# Alternative location (newer installs)
"C:\Program Files\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
```

**Google Chrome:**
```bash
# Windows Command Prompt
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# PowerShell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# Alternative location (32-bit installs)
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**Important**: Do NOT use `--user-data-dir` parameter as this would create a new profile without your Thomson Reuters login data. The default profile preserves all authentication and login sessions.

### VS Code Integration
- **Tasks configuration** for build and run commands
- **Debug configuration** for development and testing
- **Extensions** for TypeScript and MCP development
- **Terminal integration** for seamless workflow

## Usage Examples

### Basic Query
```bash
# Terminal command
mcp-agent "What are the current trends in renewable energy investments?"

# Expected flow:
1. Connect to Edge browser
2. Navigate to Thomson Reuters AI portal
3. Verify authentication
4. Select Claude Sonnet 4
5. Submit query
6. Return formatted response
```

### Status Check
```bash
# Check portal accessibility
mcp-agent --status

# Expected output:
✓ Browser connection: Active
✓ Portal authentication: Valid
✓ Available models: Claude Sonnet 4, GPT-4, etc.
✓ Session expires: 2024-12-15 14:30:00
```

## Debugging & Troubleshooting

### Common Issues
1. **Browser Connection Failed**: Check if your browser (Edge or Chrome) is running with debugging port
2. **Authentication Required**: User needs to log in to Thomson Reuters portal
3. **Portal UI Changed**: Update DOM selectors and interaction patterns
4. **Rate Limited**: Implement backoff and retry logic
5. **Session Expired**: Detect and prompt for re-authentication

### Debug Features
- **Screenshot capture** on errors for visual debugging
- **DOM inspection** to verify portal structure
- **Network monitoring** for API calls and responses
- **Performance metrics** for optimization

## Performance Considerations

### Response Time Targets
- **Browser connection**: < 2 seconds
- **Portal navigation**: < 5 seconds
- **Query submission**: < 1 second
- **Response extraction**: < 30 seconds (depends on AI model)

### Resource Management
- **Memory usage**: Monitor and cleanup browser resources
- **Connection pooling**: Reuse browser connections efficiently
- **Timeout handling**: Prevent hanging operations
- **Error recovery**: Graceful degradation on failures

## Deployment & Maintenance

### Version Control
- **Git workflow** with feature branches
- **Semantic versioning** for releases
- **Changelog** maintenance for updates
- **Documentation** updates with code changes

### Monitoring
- **Health checks** for browser and portal connectivity
- **Usage metrics** for performance optimization
- **Error tracking** for issue identification
- **Audit logs** for compliance reporting

## Future Enhancements

### Potential Features
- **Multiple AI models** support beyond Claude Sonnet 4
- **Conversation history** management
- **Batch query processing** for multiple questions
- **Custom prompt templates** for specific use cases
- **Integration with other Thomson Reuters tools**

### Architecture Evolution
- **Plugin system** for extensibility
- **Configuration management** for different environments
- **API exposure** for other internal tools
- **Performance optimization** and caching strategies

## Success Criteria

The MCP AI Portal Agent is considered successful when:
1. **Reliable connection** to Edge browser (>95% success rate)
2. **Seamless authentication** handling without credential storage
3. **Accurate query processing** with proper response extraction
4. **Error resilience** with graceful failure handling
5. **Performance targets** met for response times
6. **Security compliance** with Thomson Reuters policies
7. **User-friendly interface** with clear status and error messages

## Support & Resources

### Internal Resources
- Thomson Reuters AI portal documentation
- Company security policies and guidelines
- IT support for browser configuration issues
- Development team for architecture decisions

### External Resources
- MCP Protocol specification
- Puppeteer documentation for browser automation
- TypeScript best practices
- Node.js security guidelines

Remember: This agent operates in a corporate environment with strict security requirements. Always prioritize security, compliance, and reliability over features or performance optimizations.