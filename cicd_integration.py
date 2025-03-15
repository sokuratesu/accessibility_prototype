"""
CI/CD integration for running tests in CI/CD pipelines.
"""

import os
import sys
import json
import argparse
import logging
from typing import List, Dict, Any, Optional


class CICDRunner:
    """Runner for CI/CD environments."""

    def __init__(self, config_file=None):
        """Initialize the CI/CD runner.

        Args:
            config_file (str, optional): Path to config file
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from file.

        Returns:
            dict: Configuration
        """
        if not self.config_file or not os.path.exists(self.config_file):
            return {
                "urls": [],
                "browsers": ["chrome"],
                "screen_sizes": [
                    {"name": "Desktop", "width": 1366, "height": 768}
                ],
                "testers": ["axe"],
                "report_dir": "reports",
                "parallel": True,
                "max_workers": 4,
                "visual_diff": True,
                "reference_browser": "chrome"
            }

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {}

    def prepare_environment(self):
        """Prepare the environment for testing.

        Returns:
            bool: True if environment is prepared successfully
        """
        try:
            # Check for required dependencies
            from progressive_enhancement import BrowserAvailabilityChecker

            # Check for available browsers
            checker = BrowserAvailabilityChecker()
            available_browsers = checker.get_available_browsers()

            if not available_browsers:
                self.logger.error("No supported browsers available. Cannot run tests.")
                return False

            self.logger.info(f"Available browsers: {available_browsers}")

            # Create output directory
            os.makedirs(self.config.get("report_dir", "reports"), exist_ok=True)

            return True

        except ImportError as e:
            self.logger.error(f"Missing required dependency: {str(e)}")
            return False

        except Exception as e:
            self.logger.error(f"Error preparing environment: {str(e)}")
            return False

    def run(self):
        """Run tests in CI/CD environment.

        Returns:
            dict: Test results
        """
        try:
            if not self.prepare_environment():
                return {"error": "Failed to prepare environment"}

            # Import required modules
            from config.config_manager import ConfigManager
            from core.test_orchestrator import AccessibilityTestOrchestrator
            from utils.browser_testing_helper import BrowserTestingManager
            from testers.axe_tester import AxeAccessibilityTester
            from testers.wave_tester import WaveAccessibilityTester
            from testers.lighthouse_tester import LighthouseAccessibilityTester
            from testers.pa11y_tester import Pa11yAccessibilityTester
            from testers.htmlcs_tester import HTMLCSAccessibilityTester
            from testers.japanese_tester import JapaneseAccessibilityTester
            from testers.w3c_tester import W3CTester
            from testers.wcag22_tester import WCAG22Tester
            from progressive_enhancement import GracefulBrowserDriver
            from visual_diff_tool import VisualDiffTool
            from parallel_testing import ParallelTestRunner

            # Initialize config manager
            config_manager = ConfigManager()

            # Initialize test orchestrator
            orchestrator = AccessibilityTestOrchestrator()

            # Register testers
            tester_mapping = {
                "axe": AxeAccessibilityTester,
                "wave": WaveAccessibilityTester,
                "lighthouse": LighthouseAccessibilityTester,
                "pa11y": Pa11yAccessibilityTester,
                "htmlcs": HTMLCSAccessibilityTester,
                "japanese_a11y": JapaneseAccessibilityTester,
                "w3c_tools": W3CTester,
                "wcag22": WCAG22Tester
            }

            testers = self.config.get("testers", ["axe"])
            for tester_id in testers:
                if tester_id in tester_mapping:
                    if tester_id == "wave":
                        api_key = config_manager.get_api_key("wave") or os.environ.get("WAVE_API_KEY")
                        if api_key:
                            orchestrator.register_tester(tester_id, tester_mapping[tester_id](api_key=api_key))
                        else:
                            self.logger.warning("WAVE API key not found. Skipping WAVE testing.")
                    else:
                        orchestrator.register_tester(tester_id, tester_mapping[tester_id]())
                else:
                    self.logger.warning(f"Unknown tester: {tester_id}")

            # Prepare browser driver with graceful degradation
            browser_driver = GracefulBrowserDriver()

            # Filter to available browsers
            browsers = browser_driver.filter_available_browsers(self.config.get("browsers", ["chrome"]))

            if not browsers:
                return {"error": "No available browsers to test with"}

            # Prepare screen sizes
            screen_sizes = []
            for size in self.config.get("screen_sizes", [{"name": "Desktop", "width": 1366, "height": 768}]):
                screen_sizes.append((size["name"], size["width"], size["height"]))

            # Prepare URLs
            urls = self.config.get("urls", [])
            if not urls:
                return {"error": "No URLs specified for testing"}

            # Create report directory
            report_dir = self.config.get("report_dir", "reports")
            os.makedirs(report_dir, exist_ok=True)

            # Run tests
            all_results = {}

            if self.config.get("parallel", True):
                # Use parallel testing
                parallel_runner = ParallelTestRunner(max_workers=self.config.get("max_workers", 4))

                # Define test function for parallel execution
                def test_function(url, browser, screen_size, testers, output_dir, w3c_subtests=None):
                    screen_size_name, width, height = screen_size
                    size_key = f"{screen_size_name}_{width}x{height}"
                    browser_dir = os.path.join(output_dir, browser)
                    size_dir = os.path.join(browser_dir, size_key)
                    os.makedirs(size_dir, exist_ok=True)

                    # Create a driver for this browser
                    driver = browser_driver.create_driver(browser)

                    try:
                        # Resize window
                        driver.set_window_size(width, height)

                        # Run tests
                        result = orchestrator.run_tests(
                            url,
                            testers,
                            size_dir,
                            w3c_subtests
                        )

                        # Return the result
                        return {
                            "tools": result
                        }

                    finally:
                        driver.quit()

                # Run all URLs in parallel
                for url in urls:
                    all_results[url] = parallel_runner.run_browser_tests_in_parallel(
                        url=url,
                        testers=testers,
                        browsers=browsers,
                        screen_sizes=screen_sizes,
                        test_function=test_function,
                        test_dir=os.path.join(report_dir,
                                              url.replace("https://", "").replace("http://", "").replace("/", "_")),
                        w3c_subtests=self.config.get("w3c_subtests")
                    )

            else:
                # Run tests sequentially
                for url in urls:
                    url_results = {
                        "browsers": {}
                    }

                    for browser in browsers:
                        url_results["browsers"][browser] = {"screen_sizes": {}}

                        for size_name, width, height in screen_sizes:
                            size_key = f"{size_name}_{width}x{height}"

                            # Create directories
                            browser_dir = os.path.join(report_dir,
                                                       url.replace("https://", "").replace("http://", "").replace("/",
                                                                                                                  "_"),
                                                       browser)
                            size_dir = os.path.join(browser_dir, size_key)
                            os.makedirs(size_dir, exist_ok=True)

                            # Create driver
                            driver = browser_driver.create_driver(browser)

                            try:
                                # Resize window
                                driver.set_window_size(width, height)

                                # Run tests
                                test_results = orchestrator.run_tests(
                                    url,
                                    testers,
                                    size_dir,
                                    self.config.get("w3c_subtests")
                                )

                                # Store results
                                url_results["browsers"][browser]["screen_sizes"][size_key] = {
                                    "tools": test_results
                                }

                            finally:
                                driver.quit()

                    # Store URL results
                    all_results[url] = url_results

            # Generate visual diff if enabled
            if self.config.get("visual_diff", True):
                self.logger.info("Generating visual diffs...")

                diff_tool = VisualDiffTool()

                for url in urls:
                    url_dir = os.path.join(report_dir,
                                           url.replace("https://", "").replace("http://", "").replace("/", "_"))
                    diff_dir = os.path.join(url_dir, "diffs")
                    os.makedirs(diff_dir, exist_ok=True)

                    # Collect screenshot directories
                    screenshot_dirs = {}
                    for browser in browsers:
                        browser_screenshots = os.path.join(url_dir, browser, "screenshots") if os.path.exists(
                            os.path.join(url_dir, browser, "screenshots")) else None
                        if browser_screenshots:
                            screenshot_dirs[browser] = browser_screenshots

                    # Generate diffs
                    if len(screenshot_dirs) > 1:
                        reference_browser = self.config.get("reference_browser", browsers[0])
                        diff_results = diff_tool.batch_compare_browser_screenshots(
                            screenshot_dirs=screenshot_dirs,
                            output_dir=diff_dir,
                            reference_browser=reference_browser
                        )

                        # Add diff results to main results
                        if diff_results and "error" not in diff_results:
                            for screenshot_name, screenshot_diffs in diff_results.get("comparisons", {}).items():
                                for browser, diff_result in screenshot_diffs.items():
                                    # Extract size and page information from screenshot name
                                    parts = screenshot_name.split("_")
                                    if len(parts) >= 3:
                                        size_name = parts[1]
                                        # Find the corresponding screen size
                                        for screen_size in screen_sizes:
                                            if screen_size[0] == size_name:
                                                size_key = f"{size_name}_{screen_size[1]}x{screen_size[2]}"
                                                if browser in all_results[url]["browsers"] and size_key in \
                                                        all_results[url]["browsers"][browser]["screen_sizes"]:
                                                    all_results[url]["browsers"][browser]["screen_sizes"][size_key][
                                                        "screenshot_diff"] = diff_result

            # Generate combined report
            report_path = os.path.join(report_dir, "accessibility_report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2)

            # Return summary
            return {
                "success": True,
                "urls_tested": len(urls),
                "browsers_used": browsers,
                "testers_used": testers,
                "report_path": report_path
            }

        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            return {
                "error": str(e)
            }


def setup_cli_parser():
    """Set up command-line argument parser.

    Returns:
        ArgumentParser: Argument parser
    """
    parser = argparse.ArgumentParser(description="Run accessibility tests in CI/CD environment")

    parser.add_argument(
        "--config",
        help="Path to configuration file",
        default="cicd_config.json"
    )

    parser.add_argument(
        "--urls",
        nargs="+",
        help="URLs to test",
        default=[]
    )

    parser.add_argument(
        "--browsers",
        nargs="+",
        help="Browsers to test with",
        default=["chrome"]
    )

    parser.add_argument(
        "--testers",
        nargs="+",
        help="Testers to use",
        default=["axe"]
    )

    parser.add_argument(
        "--report-dir",
        help="Directory for reports",
        default="reports"
    )

    parser.add_argument(
        "--wave-api-key",
        help="WAVE API key"
    )

    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel testing"
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        help="Maximum worker threads for parallel testing",
        default=4
    )

    parser.add_argument(
        "--no-visual-diff",
        action="store_true",
        help="Disable visual diff generation"
    )

    parser.add_argument(
        "--reference-browser",
        help="Reference browser for visual diff",
        default="chrome"
    )

    parser.add_argument(
        "--desktop",
        action="store_true",
        help="Add desktop screen size (1366x768)"
    )

    parser.add_argument(
        "--tablet",
        action="store_true",
        help="Add tablet screen size (768x1024)"
    )

    parser.add_argument(
        "--mobile",
        action="store_true",
        help="Add mobile screen size (375x667)"
    )

    parser.add_argument(
        "--custom-size",
        nargs=3,
        action="append",
        metavar=("NAME", "WIDTH", "HEIGHT"),
        help="Add custom screen size (e.g., --custom-size Large 1920 1080)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser


def main():
    """Main entry point for CI/CD runner."""
    # Parse command-line arguments
    parser = setup_cli_parser()
    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create config from arguments
    config = {}

    # If config file exists, load it
    if os.path.exists(args.config):
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config file: {str(e)}")

    # Override with command-line arguments
    if args.urls:
        config["urls"] = args.urls

    if args.browsers:
        config["browsers"] = args.browsers

    if args.testers:
        config["testers"] = args.testers

    if args.report_dir:
        config["report_dir"] = args.report_dir

    if args.wave_api_key:
        os.environ["WAVE_API_KEY"] = args.wave_api_key

    config["parallel"] = not args.no_parallel
    config["max_workers"] = args.max_workers
    config["visual_diff"] = not args.no_visual_diff
    config["reference_browser"] = args.reference_browser

    # Set up screen sizes
    screen_sizes = config.get("screen_sizes", [])

    if args.desktop:
        screen_sizes.append({"name": "Desktop", "width": 1366, "height": 768})

    if args.tablet:
        screen_sizes.append({"name": "Tablet", "width": 768, "height": 1024})

    if args.mobile:
        screen_sizes.append({"name": "Mobile", "width": 375, "height": 667})

    if args.custom_size:
        for size in args.custom_size:
            try:
                name, width, height = size
                screen_sizes.append({
                    "name": name,
                    "width": int(width),
                    "height": int(height)
                })
            except (ValueError, TypeError):
                print(f"Invalid custom size: {size}")

    if screen_sizes:
        config["screen_sizes"] = screen_sizes
    elif "screen_sizes" not in config:
        # Default to desktop if no sizes specified
        config["screen_sizes"] = [{"name": "Desktop", "width": 1366, "height": 768}]

    # Run tests
    runner = CICDRunner(config_file=None)
    runner.config = config

    result = runner.run()

    # Print results
    print(json.dumps(result, indent=2))

    # Return exit code
    if "error" in result:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())