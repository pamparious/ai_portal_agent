# Thomson Reuters AI Portal MCP Agent

## Overview
A Model Context Protocol (MCP) server that enables command-line access to Thomson Reuters' AI portal, specifically for interacting with Claude Sonnet 4 through browser automation.

## Problem Statement
Thomson Reuters employees need to access AI tools through a secure web portal. This project creates a programmatic interface to streamline AI interactions while maintaining security compliance.

## Goals
1. **Primary**: Enable terminal-based queries to Claude Sonnet 4 via TR AI portal
2. **Secondary**: Demonstrate MCP agent capabilities for broader automation
3. **Future**: Extend to other AI models available in the portal

## Non-Goals
- Bypassing security measures
- Storing credentials
- Creating new browser sessions
- Formatted output (keeping to plain text)

## Success Criteria
- Successfully connects to existing Edge browser
- Navigates to AI portal without re-authentication
- Submits queries and retrieves responses
- Handles errors gracefully with manual intervention option
- Complies with company AI usage policies

## User Journey
1. User types query in VS Code terminal
2. MCP agent receives query
3. Browser automation navigates to AI portal
4. Query is submitted to Claude Sonnet 4
5. Response is extracted and returned to terminal
6. User sees plain text response

## Timeline
- Phase 1: Basic setup and structure (Day 1)
- Phase 2: Browser automation proof-of-concept (Day 2)
- Phase 3: MCP server implementation (Day 3)
- Phase 4: Testing and refinement (Day 4-5)