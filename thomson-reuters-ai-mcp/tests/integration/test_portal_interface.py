import asyncio
from src.browser.edge_browser_manager import EdgeBrowserManager
from src.portal.portal_interface import PortalInterface

async def main():
    browser_manager = EdgeBrowserManager()
    try:
        await browser_manager.connect_to_existing_browser()
        await browser_manager.navigate_to_portal('https://dataandanalytics.int.thomsonreuters.com/ai-platform/ai-experiences/use/27bb41d4-140b-4f8d-9179-bc57f3efbd62')
        await asyncio.sleep(5) # Add a 5-second delay

        portal_interface = PortalInterface(browser_manager.page)

        await portal_interface.take_screenshot("portal_screenshot.png")

        # Test placeholder methods
        print("\n--- Testing PortalInterface methods ---")
        chat_detected = await portal_interface.detect_chat_interface()
        print(f"Chat interface detected: {chat_detected}")

    finally:
        await browser_manager.close_browser()

if __name__ == "__main__":
    asyncio.run(main())
