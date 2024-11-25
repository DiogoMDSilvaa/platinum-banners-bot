from constants import CHROMIUM_RASPBERRY_PATH
from pyppeteer import launch
from utils import running_in_raspberry_pi

_browser_instance = None
_page = None


async def get_browser_page():
    """
    Returns a single shared instance of the browser page.
    Launches the browser if it is not already initialized.
    """

    global _browser_instance
    global _page

    if _browser_instance is None and _page is None:
        launch_options = {
            "headless": True,
        }

        # Adjust options for Raspberry Pi
        if running_in_raspberry_pi():
            launch_options.update(
                {
                    "executablePath": CHROMIUM_RASPBERRY_PATH,
                }
            )

        _browser_instance = await launch(**launch_options)
        _page = await _browser_instance.newPage()

    return _page


async def close_browser_instance():
    """
    Closes the shared browser instance if it exists.
    """

    global _browser_instance
    if _browser_instance:
        await _browser_instance.close()
        _browser_instance = None
