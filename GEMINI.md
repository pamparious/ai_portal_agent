# Thomson Reuters AI Portal MCP Agent

## Project Purpose
This MCP agent enables programmatic access to Thomson Reuters' internal AI portal through browser automation, specifically targeting Claude Sonnet 4. It acts as a bridge between command-line tools and the web-based AI interface.

## Key Capabilities
- Connects to existing Edge browser sessions with preserved authentication
- Navigates to the TR AI portal automatically
- Submits queries to Claude Sonnet 4
- Extracts and returns responses in plain text
- Handles timeout scenarios with manual intervention options

## Technical Context
- **Platform**: Windows 11
- **Browser**: Microsoft Edge (existing profile)
- **Automation**: Playwright with CDP connection
- **Protocol**: MCP (Model Context Protocol) server
- **Language**: Python 3.9+

## Current Development Focus
Building a reliable prototype that demonstrates:
1. Successful connection to existing browser sessions
2. Navigation through SSO-protected environments
3. Interaction with dynamic chat interfaces
4. Proper MCP server implementation

## Constraints & Considerations
- Must not create new browser profiles
- Must respect Thomson Reuters AI usage policies
- 30-second timeout for manual intervention
- Plain text output only (no formatting)
- Error handling for connection and navigation failures

## Integration Points
- VS Code terminal for user interaction
- Gemini CLI as the coding assistant
- Local MCP server running on localhost
- Existing Edge browser with active sessions