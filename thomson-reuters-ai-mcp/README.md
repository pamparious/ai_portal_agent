# Thomson Reuters AI Portal MCP Agent

## Overview
This project provides a Model Context Protocol (MCP) agent that enables command-line access to the Thomson Reuters AI portal, specifically for interacting with Claude Sonnet 4 through browser automation.

## Quick Start

### Prerequisites
- Windows 11
- Python 3.9+
- Microsoft Edge browser
- Access to Thomson Reuters AI Portal

### Setup and Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
git clone https://github.com/pamparious/ai_portal_agent.git
    cd thomson-reuters-ai-mcp
    ```

2.  **Set up the Python virtual environment and install dependencies**:
    Refer to the [scripts.md](scripts.md) file for detailed instructions on setting up the virtual environment and installing all necessary Python packages.

### Running the Agent

1.  **Start Microsoft Edge with Remote Debugging Enabled**:
    It is crucial to launch Microsoft Edge with remote debugging enabled on port 9222. This allows the agent to connect to your existing browser session. Use a command similar to this, replacing the `user-data-dir` with your actual Edge profile path:
    ```bash
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\%USERNAME%\AppData\Local\Microsoft\Edge\User Data"
    ```
    *Note: Ensure you close all existing Edge instances before running this command to guarantee it launches with the specified flags.*

2.  **Start the MCP Server**:
    Open a new terminal, activate your virtual environment, and run the MCP server:
    ```bash
    python -m mcp_server.server
    ```
    The server will start and attempt to connect to the running Edge browser.

3.  **Run the Test Agent (or your MCP Client)**:
    Open another new terminal, activate your virtual environment, and run the provided test agent to send a query to the AI portal:
    ```bash
    python test_agent.py
    ```
    This script will send a sample query and print the response received from the AI portal via the MCP server.

## Project Structure

-   `mcp_server/`: Contains the MCP server implementation and browser automation logic.
    -   `browser_agent.py`: Handles Playwright browser connection and navigation.
    -   `server.py`: Implements the MCP protocol and exposes AI portal functionalities as tools.
-   `src/browser/`: Original browser management (now updated to Playwright).
-   `src/portal/`: Handles interactions with the AI portal's DOM.
-   `tests/`: Contains unit and integration tests.
-   `docs/`: Additional documentation files (e.g., `claude.md`, `project.md`, `techstack.md`, `scripts.md`, `architecture.md`).
-   `requirements.txt`: Python dependencies.
-   `test_agent.py`: A simple client to test the MCP server.

## Documentation

-   [Project Overview](project.md)
-   [Technical Stack](techstack.md)
-   [Claude Sonnet 4 Integration](claude.md)
-   [Available Scripts and Commands](scripts.md)
-   [System Architecture](architecture.md)

git clone <https://github.com/pamparious/ai_portal_agent.git>
cd thomson-reuters-ai-mcp

Start: "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\Users\%USERNAME%\AppData\Local\Microsoft\Edge\User Data"