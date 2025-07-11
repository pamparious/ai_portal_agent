"""
Configuration management for MCP AI Portal Agent
Handles environment variables and configuration settings
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class BrowserConfig:
    """Browser configuration settings"""
    debug_port: int = 9222
    user_data_dir: str = "C:\\temp\\edge-debug"
    timeout: int = 30000
    headless: bool = False
    slow_mo: int = 0


@dataclass
class PortalConfig:
    """Portal configuration settings"""
    base_url: str = "https://dataandanalytics.int.thomsonreuters.com"
    ai_platform_path: str = "/ai-platform/ai-experiences/use/27bb41d4-140b-4f8d-9179-bc57f3efbd62"
    response_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: int = 1


@dataclass
class MCPConfig:
    """MCP server configuration settings"""
    server_name: str = "thomson-reuters-ai-mcp"
    server_version: str = "1.0.0"
    log_level: str = "INFO"
    max_concurrent_requests: int = 1


@dataclass
class SecurityConfig:
    """Security configuration settings"""
    enable_input_validation: bool = True
    sanitize_responses: bool = True
    max_query_length: int = 10000
    max_response_length: int = 50000
    allowed_domains: list = None


class Config:
    """Main configuration class"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.browser = BrowserConfig()
        self.portal = PortalConfig()
        self.mcp = MCPConfig()
        self.security = SecurityConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables and config file"""
        # Load from environment variables
        self._load_from_env()
        
        # Load from config file if provided
        if self.config_file and os.path.exists(self.config_file):
            self._load_from_file()
        
        # Validate configuration
        self._validate_config()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Browser configuration
        self.browser.debug_port = int(os.getenv('MCP_BROWSER_DEBUG_PORT', self.browser.debug_port))
        self.browser.user_data_dir = os.getenv('MCP_BROWSER_USER_DATA_DIR', self.browser.user_data_dir)
        self.browser.timeout = int(os.getenv('MCP_BROWSER_TIMEOUT', self.browser.timeout))
        self.browser.headless = os.getenv('MCP_BROWSER_HEADLESS', 'false').lower() == 'true'
        self.browser.slow_mo = int(os.getenv('MCP_BROWSER_SLOW_MO', self.browser.slow_mo))
        
        # Portal configuration
        self.portal.base_url = os.getenv('MCP_PORTAL_BASE_URL', self.portal.base_url)
        self.portal.ai_platform_path = os.getenv('MCP_PORTAL_AI_PATH', self.portal.ai_platform_path)
        self.portal.response_timeout = int(os.getenv('MCP_PORTAL_RESPONSE_TIMEOUT', self.portal.response_timeout))
        self.portal.retry_attempts = int(os.getenv('MCP_PORTAL_RETRY_ATTEMPTS', self.portal.retry_attempts))
        self.portal.retry_delay = int(os.getenv('MCP_PORTAL_RETRY_DELAY', self.portal.retry_delay))
        
        # MCP configuration
        self.mcp.server_name = os.getenv('MCP_SERVER_NAME', self.mcp.server_name)
        self.mcp.server_version = os.getenv('MCP_SERVER_VERSION', self.mcp.server_version)
        self.mcp.log_level = os.getenv('MCP_LOG_LEVEL', self.mcp.log_level)
        self.mcp.max_concurrent_requests = int(os.getenv('MCP_MAX_CONCURRENT_REQUESTS', self.mcp.max_concurrent_requests))
        
        # Security configuration
        self.security.enable_input_validation = os.getenv('MCP_ENABLE_INPUT_VALIDATION', 'true').lower() == 'true'
        self.security.sanitize_responses = os.getenv('MCP_SANITIZE_RESPONSES', 'true').lower() == 'true'
        self.security.max_query_length = int(os.getenv('MCP_MAX_QUERY_LENGTH', self.security.max_query_length))
        self.security.max_response_length = int(os.getenv('MCP_MAX_RESPONSE_LENGTH', self.security.max_response_length))
        
        # Parse allowed domains
        allowed_domains_str = os.getenv('MCP_ALLOWED_DOMAINS', '')
        if allowed_domains_str:
            self.security.allowed_domains = [domain.strip() for domain in allowed_domains_str.split(',')]
        else:
            self.security.allowed_domains = ['dataandanalytics.int.thomsonreuters.com']
    
    def _load_from_file(self):
        """Load configuration from file (JSON or YAML)"""
        # TODO: Implement file-based configuration loading
        logger.info(f"Configuration file loading not yet implemented: {self.config_file}")
        pass
    
    def _validate_config(self):
        """Validate configuration values"""
        # Validate browser configuration
        if not isinstance(self.browser.debug_port, int) or self.browser.debug_port < 1024:
            raise ValueError(f"Invalid browser debug port: {self.browser.debug_port}")
        
        if not isinstance(self.browser.timeout, int) or self.browser.timeout < 1000:
            raise ValueError(f"Invalid browser timeout: {self.browser.timeout}")
        
        # Validate portal configuration
        if not self.portal.base_url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid portal base URL: {self.portal.base_url}")
        
        if not isinstance(self.portal.response_timeout, int) or self.portal.response_timeout < 1:
            raise ValueError(f"Invalid portal response timeout: {self.portal.response_timeout}")
        
        # Validate security configuration
        if not isinstance(self.security.max_query_length, int) or self.security.max_query_length < 1:
            raise ValueError(f"Invalid max query length: {self.security.max_query_length}")
        
        if not isinstance(self.security.max_response_length, int) or self.security.max_response_length < 1:
            raise ValueError(f"Invalid max response length: {self.security.max_response_length}")
        
        logger.info("Configuration validation completed successfully")
    
    def get_portal_url(self) -> str:
        """Get the full portal URL"""
        return f"{self.portal.base_url.rstrip('/')}{self.portal.ai_platform_path}"
    
    def get_browser_args(self) -> Dict[str, Any]:
        """Get browser connection arguments"""
        return {
            'endpoint_url': f'http://localhost:{self.browser.debug_port}',
            'slow_mo': self.browser.slow_mo,
            'timeout': self.browser.timeout
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'browser': {
                'debug_port': self.browser.debug_port,
                'user_data_dir': self.browser.user_data_dir,
                'timeout': self.browser.timeout,
                'headless': self.browser.headless,
                'slow_mo': self.browser.slow_mo
            },
            'portal': {
                'base_url': self.portal.base_url,
                'ai_platform_path': self.portal.ai_platform_path,
                'response_timeout': self.portal.response_timeout,
                'retry_attempts': self.portal.retry_attempts,
                'retry_delay': self.portal.retry_delay
            },
            'mcp': {
                'server_name': self.mcp.server_name,
                'server_version': self.mcp.server_version,
                'log_level': self.mcp.log_level,
                'max_concurrent_requests': self.mcp.max_concurrent_requests
            },
            'security': {
                'enable_input_validation': self.security.enable_input_validation,
                'sanitize_responses': self.security.sanitize_responses,
                'max_query_length': self.security.max_query_length,
                'max_response_length': self.security.max_response_length,
                'allowed_domains': self.security.allowed_domains
            }
        }


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance"""
    return config


def reload_config(config_file: Optional[str] = None) -> Config:
    """Reload configuration"""
    global config
    config = Config(config_file)
    return config