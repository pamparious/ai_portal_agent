"I need you to create a Python-based MCP (Model Context Protocol) server that uses Playwright to control my existing Edge browser session on Windows 11. The project should follow these phases:

PHASE 1 - Project Setup:
- Create a new project directory 'thomson-reuters-ai-mcp'
- Set up Python virtual environment for Windows
- Create project structure with proper .md documentation files
- Initialize git repository
- Create requirements.txt with: playwright, mcp, asyncio, python-dotenv

PHASE 2 - Documentation Files:
Create these markdown files following context engineering best practices:
- claude.md: Project context for AI assistants
- project.md: Project overview and goals  
- techstack.md: Technical stack details
- scripts.md: Available scripts and commands
- architecture.md: System architecture
- .claudeignore: Files to ignore

PHASE 3 - MCP Server Implementation:
- Create mcp_server/browser_agent.py using Playwright to connect to existing Edge browser
- Use playwright.chromium.connect_over_cdp() to connect to existing browser
- Implement page navigation to https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/27bb41d4-140b-4f8d-9179-bc57f3efbd62
- Add page scraping to identify chat input and response elements
- Include 30-second timeout for manual intervention if needed

PHASE 4 - MCP Protocol Integration:
- Create mcp_server/server.py implementing the MCP protocol
- Define 'ask_ai' tool that accepts text queries
- Connect browser automation to MCP server
- Handle async communication properly
- Return plain text responses

PHASE 5 - Testing and CLI:
- Create test_agent.py for command-line testing
- Add proper error handling and logging
- Create setup instructions in README.md
- Include Windows-specific Edge browser connection instructions

Important requirements:
- Must use existing Edge browser profile (not create new one)
- Must handle already logged-in sessions
- Include manual intervention window with timeout
- Output plain text only
- Follow MCP server protocol standards"