# System Architecture

## Overview
The Thomson Reuters AI Portal MCP Agent is designed as a modular system, primarily consisting of a browser automation component and an MCP server component. It facilitates interaction with the Thomson Reuters AI portal via a command-line interface.

## Components

### 1. Browser Automation (Playwright)
- **Purpose**: Manages the connection to an existing Microsoft Edge browser instance and automates interactions with the AI portal.
- **Key Responsibilities**:
    - Connecting to Edge via Chrome DevTools Protocol (CDP).
    - Navigating to the AI portal URL.
    - Identifying and interacting with DOM elements (chat input, response areas).
    - Handling page navigation and timeouts.
- **Files**: `src/browser/edge_browser_manager.py`, `src/portal/portal_interface.py`

### 2. MCP Server
- **Purpose**: Implements the Model Context Protocol to expose AI portal functionalities as tools to AI assistants.
- **Key Responsibilities**:
    - Defining and registering MCP tools (e.g., `ask_ai`).
    - Receiving tool calls from AI assistants.
    - Orchestrating browser automation based on tool calls.
    - Returning results to the AI assistant.
- **Files**: `mcp_server/server.py` (to be created), `mcp_server/browser_agent.py`

### 3. CLI Interface
- **Purpose**: Provides a command-line entry point for users to interact with the MCP agent.
- **Key Responsibilities**:
    - Parsing command-line arguments.
    - Initiating communication with the MCP server.
    - Displaying responses to the user.
- **Files**: `src/cli/main.py` (example, actual implementation might vary)

## Data Flow
1. User executes a command in the terminal (e.g., `mcp-agent "What is the stock price of TR?"`).
2. The CLI interface processes the command and sends a request to the MCP server.
3. The MCP server receives the request, identifies the appropriate tool (e.g., `ask_ai`), and calls the browser automation component.
4. The browser automation component interacts with the Edge browser:
    - Navigates to the AI portal.
    - Submits the query to Claude Sonnet 4.
    - Waits for and extracts the response.
5. The extracted response is returned from the browser automation component to the MCP server.
6. The MCP server sends the response back to the CLI interface.
7. The CLI interface displays the plain text response to the user.

## Security Considerations
- **No Credential Storage**: The system relies on an existing, authenticated browser session and does not store any user credentials.
- **CDP Connection**: Connects to Edge via CDP, which should be secured and only accessible locally.
- **Input Validation**: All user inputs should be validated to prevent injection attacks or unexpected behavior.
