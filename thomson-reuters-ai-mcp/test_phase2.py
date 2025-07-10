import asyncio
from src.browser.edge_browser_manager import EdgeBrowserManager

async def main():
    

    browser_manager = EdgeBrowserManager()
    try:
        await browser_manager.connect_to_existing_browser()
        await browser_manager.navigate_to_portal('https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/27bb41d4-140b-4f8d-9179-bc57f3efbd62')
        await asyncio.sleep(3) # Add a 3-second delay
        is_logged_in = await browser_manager.check_login_status()
        print(f'Login status: {is_logged_in}')
    finally:
        await browser_manager.close_browser()

if __name__ == "__main__":
    asyncio.run(main())
