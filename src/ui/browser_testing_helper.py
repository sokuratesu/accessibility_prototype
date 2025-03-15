"""
Browser and Screen Size testing helpers for accessibility testing.
"""
from datetime import datetime
import logging
import os
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


class BrowserType(Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"  # Safari requires specific setup on macOS


class ScreenSize:
    """Represents a screen size for testing."""

    def __init__(self, name: str, width: int, height: int, enabled: bool = True):
        """Initialize a screen size.

        Args:
            name (str): Display name (e.g., "Mobile", "Tablet", "Desktop")
            width (int): Screen width in pixels
            height (int): Screen height in pixels
            enabled (bool): Whether this screen size is enabled for testing
        """
        self.name = name
        self.width = width
        self.height = height
        self.enabled = enabled

    def __str__(self) -> str:
        return f"{self.name} ({self.width}×{self.height})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for configuration storage."""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScreenSize':
        """Create a ScreenSize from a dictionary."""
        return cls(
            name=data.get("name", "Unknown"),
            width=data.get("width", 1366),
            height=data.get("height", 768),
            enabled=data.get("enabled", True)
        )


class BrowserConfig:
    """Configuration for a browser."""

    def __init__(self, name: str, enabled: bool = True):
        """Initialize a browser configuration.

        Args:
            name (str): Browser name
            enabled (bool): Whether this browser is enabled for testing
        """
        self.name = name
        self.enabled = enabled

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for configuration storage."""
        return {
            "name": self.name,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrowserConfig':
        """Create a BrowserConfig from a dictionary."""
        return cls(
            name=data.get("name", "Chrome"),
            enabled=data.get("enabled", True)
        )


class BrowserTestingManager:
    """Manages browser instances for multi-browser testing."""

    def __init__(self):
        """Initialize the browser testing manager."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.screen_sizes = [
            ScreenSize("Mobile", 375, 667, True),
            ScreenSize("Tablet", 768, 1024, True),
            ScreenSize("Desktop", 1366, 768, True)
        ]
        self.browsers = [
            BrowserConfig("Chrome", True),
            BrowserConfig("Firefox", False),
            BrowserConfig("Edge", False),
            BrowserConfig("Safari", False)
        ]

    def load_from_config(self, config: Dict[str, Any]) -> None:
        """Load browser testing configuration.

        Args:
            config (dict): Browser configuration dictionary
        """
        if "screen_sizes" in config:
            self.screen_sizes = [
                ScreenSize.from_dict(size_data)
                for size_data in config.get("screen_sizes", [])
            ]

        if "browsers" in config:
            self.browsers = [
                BrowserConfig.from_dict(browser_data)
                for browser_data in config.get("browsers", [])
            ]

    def get_enabled_screen_sizes(self) -> List[ScreenSize]:
        """Get all enabled screen sizes.

        Returns:
            list: List of enabled ScreenSize objects
        """
        return [size for size in self.screen_sizes if size.enabled]

    def get_enabled_browsers(self) -> List[BrowserConfig]:
        """Get all enabled browsers.

        Returns:
            list: List of enabled BrowserConfig objects
        """
        return [browser for browser in self.browsers if browser.enabled]

    def create_driver(self, browser_name: str) -> Optional[webdriver.Remote]:
        """Create a WebDriver for the specified browser.

        Args:
            browser_name (str): Browser name

        Returns:
            WebDriver: Selenium WebDriver instance or None if browser not supported
        """
        browser_name = browser_name.lower()

        try:
            if browser_name == "chrome":
                options = ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                return webdriver.Chrome(
                    service=ChromeService(ChromeDriverManager().install()),
                    options=options
                )

            elif browser_name == "firefox":
                options = FirefoxOptions()
                options.add_argument("--headless")
                return webdriver.Firefox(
                    service=FirefoxService(GeckoDriverManager().install()),
                    options=options
                )

            elif browser_name == "edge":
                options = EdgeOptions()
                options.add_argument("--headless")
                return webdriver.Edge(
                    service=EdgeService(EdgeChromiumDriverManager().install()),
                    options=options
                )

            elif browser_name == "safari":
                # Safari requires specific setup on macOS
                # Note: Safari's WebDriver doesn't support headless mode
                return webdriver.Safari()

            else:
                self.logger.warning(f"Unsupported browser: {browser_name}")
                return None

        except Exception as e:
            self.logger.error(f"Error creating {browser_name} driver: {str(e)}")
            return None

    def resize_browser(self, driver: webdriver.Remote, screen_size: ScreenSize) -> None:
        """Resize browser window to the specified size.

        Args:
            driver (WebDriver): Selenium WebDriver instance
            screen_size (ScreenSize): Screen size to set
        """
        try:
            driver.set_window_size(screen_size.width, screen_size.height)
            self.logger.info(f"Resized browser to {screen_size}")
        except Exception as e:
            self.logger.error(f"Error resizing browser: {str(e)}")

    def run_multi_browser_test(self, test_function, url: str,
                               browsers: Optional[List[str]] = None,
                               screen_sizes: Optional[List[Tuple[str, int, int]]] = None) -> Dict[str, Any]:
        """Run a test across multiple browsers and screen sizes.

        Args:
            test_function: Function to run the test
            url (str): URL to test
            browsers (list, optional): List of browser names to test
            screen_sizes (list, optional): List of (name, width, height) tuples

        Returns:
            dict: Test results by browser and screen size
        """
        results = {
            "url": url,
            "results": {}
        }

        # Use enabled browsers if not specified
        if browsers is None:
            browser_configs = self.get_enabled_browsers()
            browsers = [browser.name for browser in browser_configs]

        # Use enabled screen sizes if not specified
        if screen_sizes is None:
            size_configs = self.get_enabled_screen_sizes()
            screen_sizes = [(size.name, size.width, size.height) for size in size_configs]

        for browser_name in browsers:
            results["results"][browser_name] = {}

            driver = self.create_driver(browser_name)
            if driver is None:
                results["results"][browser_name]["error"] = f"Failed to initialize {browser_name} browser"
                continue

            try:
                for size_name, width, height in screen_sizes:
                    size_key = f"{size_name}_{width}x{height}"

                    # Resize browser
                    screen_size = ScreenSize(size_name, width, height)
                    self.resize_browser(driver, screen_size)

                    # Navigate to URL
                    driver.get(url)

                    # Run the test
                    self.logger.info(f"Testing {url} in {browser_name} at {size_name} ({width}×{height})")
                    test_result = test_function(driver, url, browser_name, screen_size)

                    # Store the result
                    results["results"][browser_name][size_key] = test_result

            except Exception as e:
                self.logger.error(f"Error in {browser_name} testing: {str(e)}")
                results["results"][browser_name]["error"] = str(e)

            finally:
                driver.quit()

        return results

    def capture_screenshot(self, driver, screen_size, output_dir, name=None):
        """Capture a screenshot.

        Args:
            driver (WebDriver): Selenium WebDriver instance
            screen_size (ScreenSize): Screen size
            output_dir (str): Output directory
            name (str, optional): Screenshot name

        Returns:
            str: Path to screenshot
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name or 'screenshot'}_{screen_size.name}_{screen_size.width}x{screen_size.height}_{timestamp}.png"
            filepath = os.path.join(output_dir, filename)

            # Take screenshot
            driver.save_screenshot(filepath)
            self.logger.info(f"Captured screenshot: {filepath}")

            return filepath
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {str(e)}")
            return None