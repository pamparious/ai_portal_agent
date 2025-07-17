"""
Custom exception classes for MCP AI Portal Agent
Provides specific error types for different failure scenarios
"""


class MCPAgentError(Exception):
    """Base exception for MCP AI Portal Agent errors"""


class BrowserConnectionError(MCPAgentError):
    """Raised when browser connection fails"""


class PortalError(MCPAgentError):
    """Raised when portal interaction fails"""


class AuthenticationError(MCPAgentError):
    """Raised when authentication issues occur"""


class ModelSelectionError(MCPAgentError):
    """Raised when AI model selection fails"""


class QueryError(MCPAgentError):
    """Raised when query processing fails"""


class ResponseParsingError(MCPAgentError):
    """Raised when response parsing fails"""


class OperationTimeoutError(MCPAgentError):
    """Raised when operations timeout"""


class ConfigurationError(MCPAgentError):
    """Raised when configuration issues occur"""


class ValidationError(MCPAgentError):
    """Raised when input validation fails"""
