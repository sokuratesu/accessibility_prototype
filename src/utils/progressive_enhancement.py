"""
Progressive enhancement implementation for graceful degradation when browsers are not available.
"""

import os
import platform
import logging
import sys
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService


class BrowserAvailabilityChecker:
    """Check which browsers are available on the system."""

    def __init__(self):
        """Initialize the browser availability checker."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.available_browsers = self._check_available_browsers()

    def _check_available_browsers(self):
        """Check which browsers are installed on the system.

        Returns:
            dict: Dictionary of available browsers
        """
        available = {
            "chrome": False,
            "firefox": False,
            "edge": False,
            "safari": False
        }

        # Check Chrome
        if self._is_chrome_available():
            available["chrome"] = True

        # Check Firefox
        if self._is_firefox_available():
            available["firefox"] = True

        # Check Edge
        if self._is_edge_available():
            available["edge"] = True

        # Check Safari
        if self._is_safari_available():
            available["safari"] = True

        self.logger.info(f"Available browsers: {[b for b, v in available.items() if v]}")
        return available

    def _is_chrome_available(self):
        """Check if Chrome is available."""
        try:
            # Check for Chrome executable
            if platform.system() == "Windows":
                chrome_paths = [
                    os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                                 "Google\\Chrome\\Application\\chrome.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                                 "Google\\Chrome\\Application\\chrome.exe")
                ]
                return any(os.path.exists(path) for path in chrome_paths)

            elif platform.system() == "Darwin":  # macOS
                return os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

            elif platform.system() == "Linux":
                chrome_paths = [shutil.which("google-chrome"), shutil.which("chromium-browser")]
                return any(path is not None for path in chrome_paths)

            return False

        except Exception as e:
            self.logger.warning(f"Error checking Chrome availability: {str(e)}")
            return False

    def _is_firefox_available(self):
        """Check if Firefox is available."""
        try:
            # Check for Firefox executable
            if platform.system() == "Windows":
                firefox_paths = [
                    os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Mozilla Firefox\\firefox.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                                 "Mozilla Firefox\\firefox.exe")
                ]
                return any(os.path.exists(path) for path in firefox_paths)

            elif platform.system() == "Darwin":  # macOS
                return os.path.exists("/Applications/Firefox.app/Contents/MacOS/firefox")

            elif platform.system() == "Linux":
                return shutil.which("firefox") is not None

            return False

        except Exception as e:
            self.logger.warning(f"Error checking Firefox availability: {str(e)}")
            return False

    def _is_edge_available(self):
        """Check if Edge is available."""
        try:
            # Check for Edge executable
            if platform.system() == "Windows":
                edge_paths = [
                    os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                                 "Microsoft\\Edge\\Application\\msedge.exe"),
                    os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
                                 "Microsoft\\Edge\\Application\\msedge.exe")
                ]
                return any(os.path.exists(path) for path in edge_paths)

            elif platform.system() == "Darwin":  # macOS
                return os.path.exists("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge")

            elif platform.system() == "Linux":
                return shutil.which("microsoft-edge") is not None

            return False

        except Exception as e:
            self.logger.warning(f"Error checking Edge availability: {str(e)}")
            return False

    def _is_safari_available(self):
        """Check if Safari is available."""
        try:
            # Safari is only available on macOS
            if platform.system() == "Darwin":
                return os.path.exists("/Applications/Safari.app/Contents/MacOS/Safari")
            return False

        except Exception as e:
            self.logger.warning(f"Error checking Safari availability: {str(e)}")
            return False

    def get_available_browsers(self):
        """Get list of available browsers.

        Returns:
            list: List of available browser names
        """
        return [browser for browser, available in self.available_browsers.items() if available]

    def is_browser_available(self, browser_name):
        """Check if a specific browser is available.

        Args:
            browser_name (str): Browser name

        Returns:
            bool: True if browser is available
        """
        return self.available_browsers.get(browser_name.lower(), False)

    def get_preferred_browser(self):
        """Get the preferred browser for testing.

        Returns:
            str: Preferred browser name
        """
        # Order of preference: Chrome, Firefox, Edge, Safari
        for browser in ["chrome", "firefox", "edge", "safari"]:
            if self.available_browsers.get(browser, False):
                return browser

        return None


class GracefulBrowserDriver:
    """Provide graceful fallback for browsers."""

    def __init__(self):
        """Initialize the graceful browser driver."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.checker = BrowserAvailabilityChecker()

    def create_driver(self, browser_name):
        """Create a WebDriver for the specified browser with graceful fallback.

        Args:
            browser_name (str): Browser name

        Returns:
            WebDriver: Selenium WebDriver instance
        """
        # If browser is available, create its driver
        if self.checker.is_browser_available(browser_name):
            return self._create_specific_driver(browser_name)

        # Otherwise, find an alternative
        self.logger.warning(f"Browser {browser_name} not available. Attempting to find an alternative.")

        # Get preferred browser
        alternative = self.checker.get_preferred_browser()
        if alternative:
            self.logger.info(f"Using {alternative} as an alternative to {browser_name}")
            return self._create_specific_driver(alternative)

        # If no browsers available, raise exception
        raise Exception("No supported browsers available on this system")

    def _create_specific_driver(self, browser_name):
        """Create a WebDriver for a specific browser.

        Args:
            browser_name (str): Browser name

        Returns:
            WebDriver: Selenium WebDriver instance
        """
        browser_name = browser_name.lower()

        try:
            if browser_name == "chrome":
                from selenium.webdriver.chrome.options import Options
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")

                try:
                    from webdriver_manager.chrome import ChromeDriverManager
                    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                except ImportError:
                    return webdriver.Chrome(options=options)

            elif browser_name == "firefox":
                from selenium.webdriver.firefox.options import Options
                options = Options()
                options.add_argument("--headless")

                try:
                    from webdriver_manager.firefox import GeckoDriverManager
                    return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
                except ImportError:
                    return webdriver.Firefox(options=options)

            elif browser_name == "edge":
                from selenium.webdriver.edge.options import Options
                options = Options()
                options.add_argument("--headless")

                try:
                    from webdriver_manager.microsoft import EdgeChromiumDriverManager
                    return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
                except ImportError:
                    return webdriver.Edge(options=options)

            elif browser_name == "safari":
                # Safari doesn't support headless mode
                return webdriver.Safari()

            else:
                raise ValueError(f"Unsupported browser: {browser_name}")

        except Exception as e:
            self.logger.error(f"Error creating {browser_name} driver: {str(e)}")
            raise

    def filter_available_browsers(self, browser_names):
        """Filter list of browser names to only those available.

        Args:
            browser_names (list): List of browser names

        Returns:
            list: List of available browsers from the input list
        """
        available = []
        for browser in browser_names:
            if self.checker.is_browser_available(browser):
                available.append(browser)
            else:
                self.logger.warning(f"Browser {browser} is not available and will be skipped")

        if not available and browser_names:
            # If none of the requested browsers are available, try to use any available browser
            preferred = self.checker.get_preferred_browser()
            if preferred:
                self.logger.warning(f"No requested browsers available. Using {preferred} as fallback.")
                available.append(preferred)

        return available