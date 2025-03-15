import os
import json
from datetime import datetime
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from axe_selenium_python import Axe

from ..core.base_tester import BaseAccessibilityTester
from ..utils.report_generators import generate_html_report


class AxeAccessibilityTester(BaseAccessibilityTester):
    """Accessibility tester using Axe-core via Selenium."""

    def __init__(self, browser_type="chrome"):
        super().__init__("axe")
        self.browser_type = browser_type
        self.driver = None
        self.main_test_dir = None
        self.timestamp = None

    def _setup_driver(self):
        """Setup webdriver based on browser type."""
        if self.browser_type.lower() == "chrome":
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Optional: Run in headless mode
            return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        elif self.browser_type.lower() == "firefox":
            return webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        elif self.browser_type.lower() == "edge":
            return webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")

    def test_accessibility(self, url, test_dir=None):
        """Run accessibility test on the given URL."""
        try:
            if test_dir:
                self.main_test_dir = test_dir
            else:
                self.main_test_dir, _ = self._create_test_directory()

            self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.driver = self._setup_driver()

            # Navigate to the page
            self.driver.get(url)

            # Setup axe
            axe = Axe(self.driver)
            axe.inject()

            # Configure Axe to test for WCAG 2.2
            config = {
                "runOnly": {
                    "type": "tag",
                    "values": ["wcag2a", "wcag2aa", "wcag22a", "wcag22aa"]
                },
                "rules": {
                    "dragging": {"enabled": True},
                    "target-size": {"enabled": True},
                    "focus-not-obscured": {"enabled": True},
                    "consistent-help": {"enabled": True},
                    "redundant-entry": {"enabled": True},
                    "accessible-authentication": {"enabled": True}
                }
            }

            # Run axe accessibility checks
            results = axe.run(options=config)

            # Add metadata
            results.update({
                "tool": "axe-core",
                "url": url,
                "timestamp": self.timestamp,
                "browser": self.browser_type,
                "test_dir": self.main_test_dir,
                "total_issues": len(results["violations"])
            })

            self.reformat_data(results["passes"])
            self.reformat_data(results["violations"])
            self.reformat_data(results["incomplete"])
            self.reformat_data(results["inapplicable"])

            return results

        except Exception as e:
            self.logger.error(f"Error testing {url}: {str(e)}")
            return {
                "tool": "axe-core",
                "url": url,
                "timestamp": self.timestamp,
                "browser": self.browser_type,
                "error": str(e),
                "test_dir": self.main_test_dir
            }
        finally:
            if self.driver:
                self.driver.quit()

    @staticmethod
    def reformat_data(results: list) -> None:
        for result in results:
            #Change the descriptions so that they don't mess up html data.
            result["description"] = AxeAccessibilityTester.html_replace(result["description"])
            result["help"] = AxeAccessibilityTester.html_replace(result["help"])
            for node in result["nodes"]:
                node["html"] = AxeAccessibilityTester.html_replace(node["html"])

            #Change the results so that wcag tags and regular tags are separate.
            result["wcag_tags"] = []
            for tag in result["tags"]:
                if "wcag" in tag:
                    result["wcag_tags"].append(tag)
            for wcag_tag in result["wcag_tags"]:
                result["tags"].remove(wcag_tag)

    @staticmethod
    def html_replace(data: str) -> str:
        return (data
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
            .replace("  ", "&emsp;")
        )

    def generate_report(self, results, output_dir):
        """Generate report from axe-core results."""
        try:
            # Generate filenames
            page_id = results['url'].replace('https://', '').replace('http://', '').replace('/', '_')
            json_filename = f"axe_{self.browser_type}_{page_id}_{results['timestamp']}.json"
            html_filename = f"axe_{self.browser_type}_{page_id}_{results['timestamp']}.html"

            # Save JSON report
            json_path = os.path.join(output_dir, json_filename)
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            # Generate and save HTML report
            html_report = generate_html_report(results)
            html_path = os.path.join(output_dir, html_filename)
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)

            return {
                'json': json_path,
                'html': html_path
            }

        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return None

    def _create_test_directory(self, base_dir="Reports"):
        """Create test directory structure."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        main_test_dir = os.path.join(os.getcwd(), base_dir, f"test_run_{timestamp}")

        os.makedirs(main_test_dir, exist_ok=True)
        os.makedirs(os.path.join(main_test_dir, "json_reports"), exist_ok=True)
        os.makedirs(os.path.join(main_test_dir, "html_reports"), exist_ok=True)

        return main_test_dir, timestamp