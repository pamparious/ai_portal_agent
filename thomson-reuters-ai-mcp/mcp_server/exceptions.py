"""
Custom exception classes for MCP AI Portal Agent
Provides specific error types for different failure scenarios
"""


class MCPAgentError(Exception):
    """Base exception for MCP AI Portal Agent errors"""
    pass


class BrowserConnectionError(MCPAgentError):
    """Raised when browser connection fails"""
    pass


class PortalError(MCPAgentError):
    """Raised when portal interaction fails"""
    pass


class AuthenticationError(MCPAgentError):
    """Raised when authentication issues occur"""
    pass


class ModelSelectionError(MCPAgentError):
    """Raised when AI model selection fails"""
    pass


class QueryError(MCPAgentError):
    """Raised when query processing fails"""
    pass


class ResponseParsingError(MCPAgentError):
    """Raised when response parsing fails"""
    pass


class TimeoutError(MCPAgentError):
    """Raised when operations timeout"""
    pass


class ConfigurationError(MCPAgentError):
    """Raised when configuration issues occur"""
    pass


class ValidationError(MCPAgentError):
    """Raised when input validation fails"""
    pass