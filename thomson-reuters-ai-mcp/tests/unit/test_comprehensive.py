#!/usr/bin/env python3
"""
Comprehensive test suite for MCP AI Portal Agent
Tests all components without requiring actual browser connection
"""

import asyncio
import sys
import os
import logging
from unittest.mock import Mock, AsyncMock, patch

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("comprehensive_test")


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add_result(self, test_name: str, passed: bool, message: str = ""):
        self.results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "="*60)
        print("🎯 COMPREHENSIVE TEST RESULTS")
        print("="*60)
        
        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["message"]:
                print(f"   {result['message']}")
        
        print(f"\nTotal: {self.passed + self.failed} tests")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        
        if self.failed == 0:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {self.failed} tests failed")


def test_imports(results: TestResults):
    """Test all imports work correctly"""
    try:
        from mcp_server.browser_agent import BrowserAgent
        from mcp_server.exceptions import BrowserConnectionError
        from mcp_server.config import get_config
        from src.portal.portal_interface import PortalInterface
        from cli.terminal_interface import TerminalInterface
        
        results.add_result("Import Test", True, "All imports successful")
        
    except Exception as e:
        results.add_result("Import Test", False, f"Import failed: {e}")


def test_configuration(results: TestResults):
    """Test configuration system"""
    try:
        from mcp_server.config import get_config
        
        config = get_config()
        
        # Test configuration values
        assert config.browser.debug_port == 9222
        assert config.mcp.server_name == "thomson-reuters-ai-mcp"
        assert config.security.max_query_length == 10000
        assert "dataandanalytics.int.thomsonreuters.com" in config.get_portal_url()
        
        results.add_result("Configuration Test", True, "Configuration loaded and validated")
        
    except Exception as e:
        results.add_result("Configuration Test", False, f"Configuration failed: {e}")


def test_exceptions(results: TestResults):
    """Test custom exception classes"""
    try:
        from mcp_server.exceptions import (
            BrowserConnectionError, PortalError, AuthenticationError,
            TimeoutError, ValidationError, ConfigurationError
        )
        
        # Test exception creation and inheritance
        exc = BrowserConnectionError("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)
        
        results.add_result("Exception Test", True, "Custom exceptions working correctly")
        
    except Exception as e:
        results.add_result("Exception Test", False, f"Exception test failed: {e}")


def test_browser_agent_structure(results: TestResults):
    """Test browser agent structure without connection"""
    try:
        from mcp_server.browser_agent import BrowserAgent
        
        agent = BrowserAgent()
        
        # Test required methods exist
        assert hasattr(agent, 'ask_ai')
        assert hasattr(agent, 'check_portal_status')
        assert hasattr(agent, 'list_available_models')
        assert hasattr(agent, 'get_portal_session')
        assert hasattr(agent, 'connect_to_browser')
        assert hasattr(agent, 'close')
        
        results.add_result("Browser Agent Structure", True, "All required methods present")
        
    except Exception as e:
        results.add_result("Browser Agent Structure", False, f"Structure test failed: {e}")


def test_portal_interface_structure(results: TestResults):
    """Test portal interface structure"""
    try:
        from src.portal.portal_interface import PortalInterface
        
        # Create mock page
        mock_page = Mock()
        interface = PortalInterface(mock_page)
        
        # Test required methods exist
        assert hasattr(interface, 'detect_chat_interface')
        assert hasattr(interface, 'send_message')
        assert hasattr(interface, 'wait_for_response')
        assert hasattr(interface, 'select_claude_model')
        assert hasattr(interface, 'take_screenshot')
        assert hasattr(interface, 'get_page_info')
        
        # Test selector lists exist
        assert hasattr(interface, 'response_selectors')
        assert hasattr(interface, 'chat_input_selectors')
        assert hasattr(interface, 'send_button_selectors')
        assert len(interface.response_selectors) > 0
        assert len(interface.chat_input_selectors) > 0
        assert len(interface.send_button_selectors) > 0
        
        results.add_result("Portal Interface Structure", True, "All methods and selectors present")
        
    except Exception as e:
        results.add_result("Portal Interface Structure", False, f"Structure test failed: {e}")


def test_cli_interface_structure(results: TestResults):
    """Test CLI interface structure"""
    try:
        from cli.terminal_interface import TerminalInterface
        
        interface = TerminalInterface()
        
        # Test required methods exist
        assert hasattr(interface, 'initialize')
        assert hasattr(interface, 'cleanup')
        assert hasattr(interface, 'ask_ai')
        assert hasattr(interface, 'check_status')
        assert hasattr(interface, 'list_models')
        
        results.add_result("CLI Interface Structure", True, "All required methods present")
        
    except Exception as e:
        results.add_result("CLI Interface Structure", False, f"Structure test failed: {e}")


async def test_mock_browser_operations(results: TestResults):
    """Test browser operations with mocked components"""
    try:
        from mcp_server.browser_agent import BrowserAgent
        from src.portal.portal_interface import PortalInterface
        
        # Create browser agent with mocked components
        agent = BrowserAgent()
        
        # Mock the page and portal interface
        mock_page = AsyncMock()
        mock_page.url = "https://dataandanalytics.int.thomsonreuters.com/ai-platform/test"
        mock_page.title.return_value = "Test Portal"
        
        mock_portal = AsyncMock()
        mock_portal.send_message = AsyncMock()
        mock_portal.wait_for_response = AsyncMock(return_value="Paris is the capital of France.")
        mock_portal.detect_chat_interface = AsyncMock(return_value=True)
        mock_portal.get_page_info = AsyncMock(return_value={"url": "test", "title": "test"})
        
        # Set up the mocked components
        agent.page = mock_page
        agent.portal_interface = mock_portal
        agent.last_health_check = 1234567890
        
        # Test methods that don't require browser connection
        status = await agent.check_portal_status()
        assert status["browser_connected"] == True
        
        models = await agent.list_available_models()
        assert len(models) > 0
        
        session = await agent.get_portal_session()
        assert "current_url" in session
        
        results.add_result("Mock Browser Operations", True, "Mocked browser operations work correctly")
        
    except Exception as e:
        results.add_result("Mock Browser Operations", False, f"Mock operations failed: {e}")


async def test_configuration_validation(results: TestResults):
    """Test configuration validation"""
    try:
        from mcp_server.config import Config
        
        # Test valid configuration
        config = Config()
        assert config.browser.debug_port > 0
        assert config.portal.response_timeout > 0
        assert config.security.max_query_length > 0
        
        # Test configuration methods
        portal_url = config.get_portal_url()
        assert portal_url.startswith("https://")
        
        browser_args = config.get_browser_args()
        assert "endpoint_url" in browser_args
        assert "timeout" in browser_args
        
        config_dict = config.to_dict()
        assert "browser" in config_dict
        assert "portal" in config_dict
        assert "security" in config_dict
        
        results.add_result("Configuration Validation", True, "Configuration validation passed")
        
    except Exception as e:
        results.add_result("Configuration Validation", False, f"Configuration validation failed: {e}")


def test_error_handling_structure(results: TestResults):
    """Test error handling structure"""
    try:
        from mcp_server.exceptions import ValidationError
        from mcp_server.config import get_config
        
        config = get_config()
        
        # Test validation logic exists
        assert hasattr(config.security, 'enable_input_validation')
        assert hasattr(config.security, 'max_query_length')
        assert hasattr(config.security, 'max_response_length')
        
        # Test exception can be raised
        try:
            raise ValidationError("Test validation error")
        except ValidationError as e:
            assert "Test validation error" in str(e)
        
        results.add_result("Error Handling Structure", True, "Error handling structure is correct")
        
    except Exception as e:
        results.add_result("Error Handling Structure", False, f"Error handling test failed: {e}")


async def run_all_tests():
    """Run all comprehensive tests"""
    results = TestResults()
    
    print("🧪 Running Comprehensive MCP AI Portal Agent Tests")
    print("="*60)
    
    # Run synchronous tests
    print("\n📋 Testing Imports...")
    test_imports(results)
    
    print("📋 Testing Configuration...")
    test_configuration(results)
    
    print("📋 Testing Exception Classes...")
    test_exceptions(results)
    
    print("📋 Testing Browser Agent Structure...")
    test_browser_agent_structure(results)
    
    print("📋 Testing Portal Interface Structure...")
    test_portal_interface_structure(results)
    
    print("📋 Testing CLI Interface Structure...")
    test_cli_interface_structure(results)
    
    print("📋 Testing Error Handling Structure...")
    test_error_handling_structure(results)
    
    # Run async tests
    print("\n📋 Testing Mock Browser Operations...")
    await test_mock_browser_operations(results)
    
    print("📋 Testing Configuration Validation...")
    await test_configuration_validation(results)
    
    # Print results
    results.print_summary()
    
    return results.failed == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        if success:
            print("\n🎉 All comprehensive tests passed!")
            print("✅ MCP AI Portal Agent is ready for deployment!")
            sys.exit(0)
        else:
            print("\n⚠️  Some tests failed. Please check the results above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)