# Claude Sonnet 4 Integration

## Overview
This project integrates with Claude Sonnet 4, an AI model accessible through the Thomson Reuters AI portal. The primary goal is to enable seamless interaction with Claude Sonnet 4 via a command-line interface, leveraging browser automation.

## Interaction Flow
1. User input is received via the CLI.
2. The MCP agent navigates to the Thomson Reuters AI portal.
3. The agent identifies and interacts with the Claude Sonnet 4 chat interface.
4. User queries are submitted to Claude Sonnet 4.
5. Responses from Claude Sonnet 4 are extracted and returned to the user.

## Key Considerations
- **Existing Session**: The agent must connect to an already logged-in Edge browser session to avoid re-authentication.
- **DOM Structure**: Reliable identification of chat input fields, send buttons, and response areas within the AI portal's DOM is crucial.
- **Rate Limiting/Usage Policies**: Adherence to Thomson Reuters' internal AI usage policies and any potential rate limits imposed by the Claude Sonnet 4 interface.
- **Error Handling**: Robust error handling for network issues, element not found, and unexpected portal behavior.

## Future Enhancements
- Support for other AI models available in the portal.
- More sophisticated parsing of Claude Sonnet 4 responses.
- Integration with other internal tools or systems.