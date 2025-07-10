import asyncio
from playwright.async_api import async_playwright

class EdgeBrowserManager:
    def __init__(self):
        self.browser = None
        self.page = None
        self.playwright_instance = None

    async def connect_to_existing_browser(self):
        try:
            print('Attempting to connect to existing Edge browser via CDP...')
            self.playwright_instance = await async_playwright().start()
            self.browser = await self.playwright_instance.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print('Connected to browser.')
            
            pages = self.browser.contexts[0].pages
            self.page = pages[0] if pages else await self.browser.new_page()
            
        except Exception as e:
            print(f'Failed to connect to browser: {e}')
            print('Please ensure Edge is running with --remote-debugging-port=9222')
            raise

    async def navigate_to_portal(self, url):
        if not self.page:
            raise Exception('Page is not available. Call connect_to_existing_browser first.')
        try:
            print(f'Navigating to {url}...')
            await self.page.goto(url, timeout=60000)
            print('Navigation complete.')
        except Exception as e:
            print(f'Failed to navigate to {url}: {e}')
            raise

    async def check_login_status(self):
        if not self.page:
            raise Exception('Page is not available. Call connect_to_existing_browser first.')
        
        # Check for the presence of the user's name element using Playwright's locator
        # This selector needs to be verified based on the actual DOM of the AI portal
        user_name_locator = self.page.locator('div._user_y603u_1:has-text("Andreas Pils")')
        is_logged_in = await user_name_locator.is_visible()
        return is_logged_in

    async def close_browser(self):
        if self.browser:
            print('Disconnecting from browser...')
            await self.browser.close()
            if self.playwright_instance:
                await self.playwright_instance.stop()
            self.browser = None
            self.page = None
            self.playwright_instance = None
            print('Disconnected from browser.')