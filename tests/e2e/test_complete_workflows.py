#!/usr/bin/env python3
"""
End-to-End Tests for DexAgent Complete Workflows
This module tests complete user workflows from the frontend perspective.
"""

import asyncio
import json
import time
import uuid
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import pytest
from typing import Dict, Any, List

# Test configuration
E2E_CONFIG = {
    'frontend_url': 'http://localhost:3000',
    'backend_url': 'http://localhost:8080',
    'test_credentials': {
        'username': 'admin',
        'password': 'admin123'
    },
    'timeouts': {
        'navigation': 30000,
        'element': 10000,
        'network': 30000
    }
}

class DexAgentE2ETest:
    """Base class for E2E tests"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        
    async def setup_browser(self, headless: bool = True):
        """Setup browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        # Set timeouts
        self.page.set_default_timeout(E2E_CONFIG['timeouts']['element'])
        self.page.set_default_navigation_timeout(E2E_CONFIG['timeouts']['navigation'])
        
    async def teardown_browser(self):
        """Clean up browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
            
    async def login(self):
        """Login to the application"""
        await self.page.goto(f"{E2E_CONFIG['frontend_url']}/login")
        
        # Fill login form
        await self.page.fill('input[name="username"]', E2E_CONFIG['test_credentials']['username'])
        await self.page.fill('input[name="password"]', E2E_CONFIG['test_credentials']['password'])
        
        # Submit form
        await self.page.click('button[type="submit"]')
        
        # Wait for redirect to dashboard
        await self.page.wait_for_url('**/dashboard', timeout=E2E_CONFIG['timeouts']['navigation'])
        
    async def navigate_to_agents(self):
        """Navigate to agents page"""
        await self.page.click('a[href*="/agents"]')
        await self.page.wait_for_url('**/agents')
        
    async def navigate_to_commands(self):
        """Navigate to commands page"""
        await self.page.click('a[href*="/commands"]')
        await self.page.wait_for_url('**/commands')
        
    async def wait_for_element_with_text(self, selector: str, text: str, timeout: int = 10000):
        """Wait for element containing specific text"""
        await self.page.wait_for_function(
            f"""() => {{
                const element = document.querySelector('{selector}');
                return element && element.textContent.includes('{text}');
            }}""",
            timeout=timeout
        )

class TestCompleteUserWorkflows(DexAgentE2ETest):
    """Test complete user workflows"""
    
    async def test_complete_agent_management_workflow(self):
        """Test complete agent management workflow"""
        
        await self.setup_browser()
        
        try:
            # Login
            await self.login()
            
            # Navigate to agents page
            await self.navigate_to_agents()
            
            # Verify agents page loaded
            await self.page.wait_for_selector('[data-testid="agents-table"]')
            
            # Check if there are any agents
            agent_rows = await self.page.query_selector_all('[data-testid="agent-row"]')
            initial_agent_count = len(agent_rows)
            
            # Test agent filtering/search if available
            search_input = await self.page.query_selector('input[placeholder*="search"], input[placeholder*="filter"]')
            if search_input:
                await search_input.fill('test')
                await self.page.wait_for_timeout(1000)  # Wait for filter to apply
                
                # Clear search
                await search_input.fill('')
                await self.page.wait_for_timeout(1000)
                
            # Test agent details view
            if initial_agent_count > 0:
                # Click on first agent
                await self.page.click('[data-testid="agent-row"]:first-child')
                
                # Verify agent details page
                await self.page.wait_for_selector('[data-testid="agent-details"]')
                
                # Check for agent information sections
                await self.page.wait_for_selector('[data-testid="agent-info"]')
                await self.page.wait_for_selector('[data-testid="agent-metrics"]')
                
                # Navigate back to agents list
                await self.page.go_back()
                await self.page.wait_for_selector('[data-testid="agents-table"]')
                
            # Test refresh functionality
            refresh_button = await self.page.query_selector('[data-testid="refresh-agents"]')
            if refresh_button:
                await refresh_button.click()
                await self.page.wait_for_timeout(1000)
                
        finally:
            await self.teardown_browser()
            
    async def test_complete_command_execution_workflow(self):
        """Test complete command execution workflow"""
        
        await self.setup_browser()
        
        try:
            # Login
            await self.login()
            
            # Navigate to commands page
            await self.navigate_to_commands()
            
            # Verify commands page loaded
            await self.page.wait_for_selector('[data-testid="commands-page"]')
            
            # Test creating a new command
            create_button = await self.page.query_selector('[data-testid="create-command"]')
            if create_button:
                await create_button.click()
                
                # Fill command form
                await self.page.wait_for_selector('[data-testid="command-form"]')
                
                test_command_name = f'E2E Test Command {uuid.uuid4().hex[:8]}'
                test_command = 'Get-Date; Write-Output "E2E Test Complete"'
                
                await self.page.fill('input[name="name"]', test_command_name)
                await self.page.fill('textarea[name="command"]', test_command)
                await self.page.fill('textarea[name="description"]', 'E2E test command')
                
                # Select category if available
                category_select = await self.page.query_selector('select[name="category"]')
                if category_select:
                    await category_select.select_option('system')
                    
                # Save command
                await self.page.click('button[type="submit"]')
                
                # Wait for command to be created
                await self.page.wait_for_selector('[data-testid="commands-table"]')
                await self.wait_for_element_with_text('[data-testid="commands-table"]', test_command_name)
                
            # Test command execution if agents are available
            await self.navigate_to_agents()
            agent_rows = await self.page.query_selector_all('[data-testid="agent-row"]')
            
            if len(agent_rows) > 0:
                # Go back to commands and execute on first agent
                await self.navigate_to_commands()
                
                # Find our test command and execute it
                await self.page.wait_for_selector('[data-testid="commands-table"]')
                
                # Look for execute button
                execute_button = await self.page.query_selector('[data-testid="execute-command"]:first-child')
                if execute_button:
                    await execute_button.click()
                    
                    # Select agent for execution
                    await self.page.wait_for_selector('[data-testid="agent-selection"]')
                    await self.page.click('[data-testid="agent-option"]:first-child')
                    
                    # Execute command
                    await self.page.click('[data-testid="execute-submit"]')
                    
                    # Wait for execution to start
                    await self.page.wait_for_selector('[data-testid="execution-status"]')
                    
        finally:
            await self.teardown_browser()
            
    async def test_dashboard_monitoring_workflow(self):
        """Test dashboard monitoring and real-time updates"""
        
        await self.setup_browser()
        
        try:
            # Login
            await self.login()
            
            # Verify dashboard elements
            await self.page.wait_for_selector('[data-testid="dashboard"]')
            
            # Check for main dashboard components
            dashboard_components = [
                '[data-testid="agents-summary"]',
                '[data-testid="commands-summary"]',
                '[data-testid="system-status"]'
            ]
            
            for component in dashboard_components:
                element = await self.page.query_selector(component)
                if element:
                    await self.page.wait_for_selector(component)
                    
            # Test real-time updates by checking for periodic updates
            initial_timestamp = await self.page.text_content('[data-testid="last-updated"]') if await self.page.query_selector('[data-testid="last-updated"]') else None
            
            if initial_timestamp:
                # Wait for update
                await self.page.wait_for_timeout(5000)
                
                # Check if timestamp changed
                updated_timestamp = await self.page.text_content('[data-testid="last-updated"]')
                assert updated_timestamp != initial_timestamp, "Dashboard should update automatically"
                
            # Test navigation from dashboard
            # Click on agents summary to go to agents page
            agents_link = await self.page.query_selector('[data-testid="agents-summary"] a')
            if agents_link:
                await agents_link.click()
                await self.page.wait_for_url('**/agents')
                
                # Navigate back to dashboard
                await self.page.click('[data-testid="dashboard-link"]')
                await self.page.wait_for_url('**/dashboard')
                
        finally:
            await self.teardown_browser()
            
    async def test_settings_configuration_workflow(self):
        """Test settings and configuration workflow"""
        
        await self.setup_browser()
        
        try:
            # Login
            await self.login()
            
            # Navigate to settings
            await self.page.click('a[href*="/settings"]')
            await self.page.wait_for_url('**/settings')
            
            # Verify settings page loaded
            await self.page.wait_for_selector('[data-testid="settings-page"]')
            
            # Test AI configuration if available
            ai_section = await self.page.query_selector('[data-testid="ai-settings"]')
            if ai_section:
                # Check current AI status
                ai_status = await self.page.text_content('[data-testid="ai-status"]')
                
                # Test AI configuration form
                api_key_input = await self.page.query_selector('input[name="openai_api_key"]')
                if api_key_input:
                    current_value = await api_key_input.get_attribute('value')
                    
                    # Test form validation (enter invalid key)
                    await api_key_input.fill('invalid-key')
                    await self.page.click('[data-testid="save-ai-settings"]')
                    
                    # Should show validation error
                    await self.page.wait_for_selector('[data-testid="error-message"]')
                    
                    # Restore original value
                    if current_value:
                        await api_key_input.fill(current_value)
                        await self.page.click('[data-testid="save-ai-settings"]')
                        
            # Test general settings
            general_section = await self.page.query_selector('[data-testid="general-settings"]')
            if general_section:
                # Test timeout settings
                timeout_input = await self.page.query_selector('input[name="default_timeout"]')
                if timeout_input:
                    original_timeout = await timeout_input.get_attribute('value')
                    
                    # Change timeout value
                    await timeout_input.fill('45')
                    await self.page.click('[data-testid="save-general-settings"]')
                    
                    # Verify save success
                    await self.page.wait_for_selector('[data-testid="save-success"]')
                    
                    # Restore original value
                    if original_timeout:
                        await timeout_input.fill(original_timeout)
                        await self.page.click('[data-testid="save-general-settings"]')
                        
        finally:
            await self.teardown_browser()
            
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery scenarios"""
        
        await self.setup_browser()
        
        try:
            # Login
            await self.login()
            
            # Test network error handling
            # Intercept network requests and simulate failures
            await self.page.route('**/api/v1/agents', lambda route: route.abort())
            
            # Navigate to agents page
            await self.navigate_to_agents()
            
            # Should show error message
            await self.page.wait_for_selector('[data-testid="error-message"]')
            
            # Test retry functionality
            retry_button = await self.page.query_selector('[data-testid="retry-button"]')
            if retry_button:
                # Remove network interception
                await self.page.unroute('**/api/v1/agents')
                
                # Click retry
                await retry_button.click()
                
                # Should load successfully now
                await self.page.wait_for_selector('[data-testid="agents-table"]')
                
            # Test form validation errors
            await self.navigate_to_commands()
            
            create_button = await self.page.query_selector('[data-testid="create-command"]')
            if create_button:
                await create_button.click()
                
                # Try to submit empty form
                await self.page.click('button[type="submit"]')
                
                # Should show validation errors
                await self.page.wait_for_selector('[data-testid="validation-error"]')
                
                # Fill required fields
                await self.page.fill('input[name="name"]', 'Test Command')
                await self.page.fill('textarea[name="command"]', 'Get-Date')
                
                # Should be able to submit now
                await self.page.click('button[type="submit"]')
                
                # Should redirect back to commands list
                await self.page.wait_for_selector('[data-testid="commands-table"]')
                
        finally:
            await self.teardown_browser()

class TestAccessibilityAndUsability(DexAgentE2ETest):
    """Test accessibility and usability features"""
    
    async def test_keyboard_navigation(self):
        """Test keyboard navigation throughout the application"""
        
        await self.setup_browser()
        
        try:
            # Login using keyboard
            await self.page.goto(f"{E2E_CONFIG['frontend_url']}/login")
            
            # Tab to username field
            await self.page.keyboard.press('Tab')
            await self.page.keyboard.type(E2E_CONFIG['test_credentials']['username'])
            
            # Tab to password field
            await self.page.keyboard.press('Tab')
            await self.page.keyboard.type(E2E_CONFIG['test_credentials']['password'])
            
            # Tab to submit button and press Enter
            await self.page.keyboard.press('Tab')
            await self.page.keyboard.press('Enter')
            
            # Should be logged in
            await self.page.wait_for_url('**/dashboard')
            
            # Test navigation using keyboard
            # Tab through main navigation
            for _ in range(5):  # Assume 5 main nav items
                await self.page.keyboard.press('Tab')
                
            # Press Enter on agents link (assuming it's focused)
            await self.page.keyboard.press('Enter')
            
            # Should navigate to agents page
            await self.page.wait_for_url('**/agents')
            
        finally:
            await self.teardown_browser()
            
    async def test_responsive_design(self):
        """Test responsive design at different screen sizes"""
        
        await self.setup_browser()
        
        try:
            # Login
            await self.login()
            
            # Test different viewport sizes
            viewports = [
                {'width': 1920, 'height': 1080},  # Desktop
                {'width': 1024, 'height': 768},   # Tablet landscape
                {'width': 768, 'height': 1024},   # Tablet portrait
                {'width': 375, 'height': 667},    # Mobile
            ]
            
            for viewport in viewports:
                await self.page.set_viewport_size(viewport['width'], viewport['height'])
                
                # Test that main elements are visible
                await self.page.wait_for_selector('[data-testid="dashboard"]')
                
                # Check navigation (might be collapsed on mobile)
                nav_element = await self.page.query_selector('[data-testid="main-navigation"]')
                if nav_element:
                    is_visible = await nav_element.is_visible()
                    
                    # On mobile, navigation might be hidden initially
                    if viewport['width'] < 768 and not is_visible:
                        # Look for hamburger menu
                        menu_button = await self.page.query_selector('[data-testid="mobile-menu-button"]')
                        if menu_button:
                            await menu_button.click()
                            await self.page.wait_for_selector('[data-testid="main-navigation"]')
                            
                # Test that tables are scrollable on small screens
                await self.navigate_to_agents()
                table = await self.page.query_selector('[data-testid="agents-table"]')
                if table:
                    # Table should be visible and scrollable
                    await self.page.wait_for_selector('[data-testid="agents-table"]')
                    
        finally:
            await self.teardown_browser()

class TestPerformanceMetrics(DexAgentE2ETest):
    """Test frontend performance metrics"""
    
    async def test_page_load_performance(self):
        """Test page load performance"""
        
        await self.setup_browser()
        
        try:
            # Measure login page load time
            start_time = time.time()
            await self.page.goto(f"{E2E_CONFIG['frontend_url']}/login")
            await self.page.wait_for_load_state('networkidle')
            login_load_time = time.time() - start_time
            
            assert login_load_time < 5, f"Login page took too long to load: {login_load_time}s"
            
            # Login
            await self.login()
            
            # Measure dashboard load time
            start_time = time.time()
            await self.page.wait_for_load_state('networkidle')
            dashboard_load_time = time.time() - start_time
            
            assert dashboard_load_time < 5, f"Dashboard took too long to load: {dashboard_load_time}s"
            
            # Measure agents page load time
            start_time = time.time()
            await self.navigate_to_agents()
            await self.page.wait_for_load_state('networkidle')
            agents_load_time = time.time() - start_time
            
            assert agents_load_time < 5, f"Agents page took too long to load: {agents_load_time}s"
            
            # Test client-side navigation performance
            start_time = time.time()
            await self.navigate_to_commands()
            await self.page.wait_for_selector('[data-testid="commands-page"]')
            commands_nav_time = time.time() - start_time
            
            assert commands_nav_time < 2, f"Client-side navigation too slow: {commands_nav_time}s"
            
        finally:
            await self.teardown_browser()
            
    async def test_memory_usage(self):
        """Test frontend memory usage"""
        
        await self.setup_browser()
        
        try:
            # Login
            await self.login()
            
            # Get initial memory usage
            initial_memory = await self.page.evaluate('performance.memory.usedJSHeapSize')
            
            # Navigate through multiple pages
            pages = ['agents', 'commands', 'settings', 'dashboard']
            
            for page_name in pages * 3:  # Navigate multiple times
                if page_name == 'agents':
                    await self.navigate_to_agents()
                elif page_name == 'commands':
                    await self.navigate_to_commands()
                elif page_name == 'settings':
                    await self.page.click('a[href*="/settings"]')
                elif page_name == 'dashboard':
                    await self.page.click('a[href*="/dashboard"]')
                    
                await self.page.wait_for_timeout(1000)
                
            # Get final memory usage
            final_memory = await self.page.evaluate('performance.memory.usedJSHeapSize')
            
            # Memory shouldn't grow excessively
            memory_growth = final_memory - initial_memory
            memory_growth_mb = memory_growth / 1024 / 1024
            
            assert memory_growth_mb < 50, f"Memory usage grew too much: {memory_growth_mb}MB"
            
        finally:
            await self.teardown_browser()

# Test runner for async tests
@pytest.mark.asyncio
async def test_complete_agent_management():
    test = TestCompleteUserWorkflows()
    await test.test_complete_agent_management_workflow()

@pytest.mark.asyncio
async def test_complete_command_execution():
    test = TestCompleteUserWorkflows()
    await test.test_complete_command_execution_workflow()

@pytest.mark.asyncio
async def test_dashboard_monitoring():
    test = TestCompleteUserWorkflows()
    await test.test_dashboard_monitoring_workflow()

@pytest.mark.asyncio
async def test_settings_configuration():
    test = TestCompleteUserWorkflows()
    await test.test_settings_configuration_workflow()

@pytest.mark.asyncio
async def test_error_handling():
    test = TestCompleteUserWorkflows()
    await test.test_error_handling_and_recovery()

@pytest.mark.asyncio
async def test_keyboard_navigation():
    test = TestAccessibilityAndUsability()
    await test.test_keyboard_navigation()

@pytest.mark.asyncio
async def test_responsive_design():
    test = TestAccessibilityAndUsability()
    await test.test_responsive_design()

@pytest.mark.asyncio
async def test_page_performance():
    test = TestPerformanceMetrics()
    await test.test_page_load_performance()

@pytest.mark.asyncio
async def test_memory_performance():
    test = TestPerformanceMetrics()
    await test.test_memory_usage()

# Test runner
if __name__ == '__main__':
    import sys
    
    # Run with pytest
    sys.exit(pytest.main([__file__, '-v', '--tb=short']))