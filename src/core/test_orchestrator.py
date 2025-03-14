"""
Test orchestrator module
Manages multiple accessibility tests and coordinates their execution.
"""

import os
import logging
import json
import re
import time
from datetime import datetime
import uuid

from ..utils.report_generators import CombinedReportGenerator, generate_summary_report


class AccessibilityTestOrchestrator:
    """Orchestrates multiple accessibility testers."""

    def __init__(self):
        """Initialize the orchestrator."""
        self.testers = {}
        self.results = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self.japanese_config = {}

    def register_tester(self, tester_id, tester):
        """Register a tester.

        Args:
            tester_id (str): ID for the tester
            tester (BaseAccessibilityTester): The tester instance
        """
        self.testers[tester_id] = tester
        self.logger.info(f"Registered tester: {tester_id}")

    def configure_japanese_testing(self, enabled=False, form_zero=False, ruby_check=True, encoding="utf-8"):
        """Configure Japanese-specific testing options.

        Args:
            enabled (bool): Enable Japanese testing
            form_zero (bool): Enable form zero testing
            ruby_check (bool): Enable ruby text checking
            encoding (str): Preferred encoding
        """
        self.japanese_config = {
            "enabled": enabled,
            "form_zero": form_zero,
            "ruby_check": ruby_check,
            "encoding": encoding
        }
        self.logger.info("Japanese testing configured")

    def run_tests(self, url, tester_ids=None, test_dir=None, w3c_subtests=None):
        """Run accessibility tests.

        Args:
            url (str): The URL to test
            tester_ids (list, optional): List of tester IDs to use. If None, use all registered testers.
            test_dir (str, optional): Directory to save test results. If None, create a new directory.

        Returns:
            dict: Test results for each tester
        """
        # Create test directory if not provided
        if test_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_dir = os.path.join(os.getcwd(), "reports")
            test_id = f"{timestamp}_{uuid.uuid4().hex[:8]}"
            test_dir = os.path.join(base_dir, test_id)

        os.makedirs(test_dir, exist_ok=True)

        # Determine which testers to use
        if tester_ids is None:
            tester_ids = list(self.testers.keys())
        else:
            # Filter to only registered testers
            tester_ids = [tid for tid in tester_ids if tid in self.testers]

        if not tester_ids:
            self.logger.warning("No valid testers specified")
            return {}

        # Run each tester
        results = {}
        for tester_id in tester_ids:
            try:
                self.logger.info(f"Running {tester_id} on {url}")
                tester = self.testers[tester_id]

                # If this is the Japanese tester, pass the configuration
                if tester_id == "japanese_a11y" and self.japanese_config.get("enabled"):
                    if hasattr(tester, "form_zero_enabled"):
                        tester.form_zero_enabled = self.japanese_config.get("form_zero", False)
                    if hasattr(tester, "ruby_checkbox") and hasattr(tester.ruby_checkbox, "value"):
                        tester.ruby_checkbox.value = self.japanese_config.get("ruby_check", True)

                # Run the test
                # self.logger.info(f"Running {tester_id} on {url}")
                start_time = time.time()

                # test_result = tester.test_accessibility(url, test_dir)
                # Special handling for W3C tester with sub-tests
                if tester_id == "w3c_tools" and w3c_subtests is not None:
                    test_result = tester.test_accessibility(
                        url,
                        test_dir,
                        enabled_tests=w3c_subtests  # Pass the enabled subtests
                    )
                else:
                    # Run other testers normally
                    test_result = tester.test_accessibility(url, test_dir)

                duration = time.time() - start_time
                self.logger.info(f"Completed {tester_id} in {duration:.2f} seconds")

                # Generate reports
                tester_output_dir = os.path.join(test_dir, tester_id)
                os.makedirs(tester_output_dir, exist_ok=True)
                report_paths = tester.generate_report(test_result, tester_output_dir)

                if report_paths:
                    test_result["reports"] = report_paths

                # Store results
                results[tester_id] = test_result

            except Exception as e:
                error_message = f"Error running {tester_id}: {str(e)}"
                self.logger.error(error_message)
                results[tester_id] = {
                    "tool": tester_id,
                    "url": url,
                    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "error": error_message,
                    "test_dir": test_dir
                }

        # Generate combined and summary reports
        self._generate_combined_reports(results, test_dir)

        # Save all results
        all_results_path = os.path.join(test_dir, "all_results.json")
        with open(all_results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        return results

    def _generate_combined_reports(self, results, test_dir):
        """Generate combined reports from all tester results.

        Args:
            results (dict): Results from all testers
            test_dir (str): Directory to save reports
        """
        try:
            # Create combined report generator
            combined_generator = CombinedReportGenerator(test_dir)

            # Generate combined report
            combined_path = combined_generator.generate_combined_report({
                results.get("url", "unknown_url"): results
            })

            # Generate summary report
            summary_path = generate_summary_report({
                results.get("url", "unknown_url"): results
            }, test_dir)

            self.logger.info(f"Generated combined reports in {test_dir}")
            return {
                "combined": combined_path,
                "summary": summary_path
            }

        except Exception as e:
            self.logger.error(f"Error generating combined reports: {str(e)}")
            return None

    # def batch_test_urls(self, urls, tester_ids=None, responsive=False, viewports=None, browsers=None):
    #     """Run tests on multiple URLs.
    #
    #     Args:
    #         urls (list): List of URLs to test
    #         tester_ids (list, optional): List of tester IDs to use
    #
    #     Returns:
    #         dict: Results for each URL
    #         :param browsers:
    #         :param viewports:
    #         :param responsive:
    #     """
    #     # Create a main test directory
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #     base_dir = os.path.join(os.getcwd(), "reports")
    #     test_id = f"batch_{timestamp}_{uuid.uuid4().hex[:8]}"
    #     main_test_dir = os.path.join(base_dir, test_id)
    #     os.makedirs(main_test_dir, exist_ok=True)
    #
    #     # Initialize viewports and browsers
    #     if responsive and not viewports:
    #         viewports = [320, 768, 1200]
    #
    #     if not browsers:
    #         browsers = ["chrome"]
    #
    #     # Run tests for each URL
    #     all_results = {}
    #     for i, url in enumerate(urls):
    #         self.logger.info(f"Testing URL {i + 1}/{len(urls)}: {url}")
    #
    #         # Create a subdirectory for this URL
    #         url_safe_name = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
    #         if len(url_safe_name) > 50:  # Truncate if too long
    #             url_safe_name = url_safe_name[:50]
    #         url_dir = os.path.join(main_test_dir, f"{i + 1}_{url_safe_name}")
    #
    #         # Run the tests
    #         results = self.run_tests(url, tester_ids, url_dir)
    #         all_results[url] = results
    #
    #     # Generate overall summary
    #     self.logger.info("Generating batch summary report")
    #     summary_path = generate_summary_report(all_results, main_test_dir)
    #
    #     # Save all results
    #     all_results_path = os.path.join(main_test_dir, "all_urls_results.json")
    #     with open(all_results_path, 'w', encoding='utf-8') as f:
    #         json.dump({url: {t: r for t, r in results.items() if "reports" not in t}
    #                    for url, results in all_results.items()}, f, indent=2)
    #
    #     self.logger.info(f"Batch testing complete. Summary: {summary_path}")
    #
    #     # Add the test directory to results for UI to access
    #     for url in all_results:
    #         for tool in all_results[url]:
    #             all_results[url][tool]["test_dir"] = main_test_dir
    #
    #     return all_results

    # In src/core/test_orchestrator.py

    def batch_test_urls(self, urls, tester_ids=None, responsive=False, viewports=None, browsers=None):
        """Enhanced batch testing with support for responsive and multi-browser testing.

        Args:
            urls (list): List of URLs to test
            tester_ids (list, optional): List of tester IDs to use
            responsive (bool): Whether to test at different viewport widths
            viewports (list, optional): List of viewport widths to test at
            browsers (list, optional): List of browsers to test with

        Returns:
            dict: Results organized by URL, browser, and viewport
        """
        # Create main test directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_id = f"batch_test_{timestamp}_{uuid.uuid4().hex[:8]}"
        base_dir = os.path.join(os.getcwd(), "reports")
        test_dir = os.path.join(base_dir, test_id)
        os.makedirs(test_dir, exist_ok=True)

        # Initialize viewports and browsers
        if responsive and not viewports:
            viewports = [320, 768, 1200]

        if not browsers:
            browsers = ["chrome"]

        # Determine which testers to use
        if tester_ids is None:
            tester_ids = list(self.testers.keys())
        else:
            # Filter to only registered testers
            tester_ids = [tid for tid in tester_ids if tid in self.testers]

        # Run tests for each URL
        all_results = {}
        for i, url in enumerate(urls):
            self.logger.info(f"Testing URL {i + 1}/{len(urls)}: {url}")

            # Create URL-specific directory
            url_safe = re.sub(r'[^a-zA-Z0-9]', '_', url)
            url_dir = os.path.join(test_dir, f"{i + 1}_{url_safe[:50]}")
            os.makedirs(url_dir, exist_ok=True)

            # Store results for this URL
            url_results = {}

            # Test with each browser
            for browser in browsers:
                # Store results for this browser
                browser_results = {}

                # Set browser for relevant testers
                for tester_id in tester_ids:
                    if tester_id in self.testers:
                        tester = self.testers[tester_id]
                        if hasattr(tester, 'browser_type'):
                            # Remember original browser
                            original_browser = tester.browser_type
                            # Set browser for this test
                            tester.browser_type = browser

                # Test at each viewport if responsive testing is enabled
                if responsive and viewports:
                    for viewport in viewports:
                        self.logger.info(f"Testing {url} with {browser} at {viewport}px width")

                        # Create subdirectory for this viewport
                        viewport_dir = os.path.join(url_dir, f"{browser}_{viewport}px")
                        os.makedirs(viewport_dir, exist_ok=True)

                        # Set viewport for browser-based testers
                        for tester_id in tester_ids:
                            if tester_id in self.testers:
                                tester = self.testers[tester_id]
                                if hasattr(tester, 'driver') and tester.driver:
                                    # Get original size
                                    original_size = tester.driver.get_window_size()
                                    # Set new viewport size
                                    tester.driver.set_window_size(viewport, original_size['height'])

                        # Run the tests
                        try:
                            results = self.run_tests(url, tester_ids, viewport_dir)
                            browser_results[viewport] = results
                        except Exception as e:
                            self.logger.error(f"Error testing {url} with {browser} at {viewport}px: {str(e)}")
                            browser_results[viewport] = {
                                "error": str(e),
                                "url": url,
                                "browser": browser,
                                "viewport": viewport
                            }

                        # Reset viewport
                        for tester_id in tester_ids:
                            if tester_id in self.testers:
                                tester = self.testers[tester_id]
                                if hasattr(tester, 'driver') and tester.driver:
                                    # Restore original size
                                    tester.driver.set_window_size(original_size['width'], original_size['height'])
                else:
                    # Standard test (no responsive)
                    self.logger.info(f"Testing {url} with {browser}")

                    # Create subdirectory for this browser
                    browser_dir = os.path.join(url_dir, browser)
                    os.makedirs(browser_dir, exist_ok=True)

                    # Run the tests
                    try:
                        results = self.run_tests(url, tester_ids, browser_dir)
                        browser_results["standard"] = results
                    except Exception as e:
                        self.logger.error(f"Error testing {url} with {browser}: {str(e)}")
                        browser_results["standard"] = {
                            "error": str(e),
                            "url": url,
                            "browser": browser
                        }

                # Store results for this browser
                url_results[browser] = browser_results

                # Reset browser for testers
                for tester_id in tester_ids:
                    if tester_id in self.testers:
                        tester = self.testers[tester_id]
                        if hasattr(tester, 'browser_type') and 'original_browser' in locals():
                            tester.browser_type = original_browser

            # Store results for this URL
            all_results[url] = url_results

        # Generate summary report
        summary_path = os.path.join(test_dir, "batch_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": timestamp,
                "urls_tested": len(urls),
                "browsers_tested": browsers,
                "viewports_tested": viewports if responsive else "standard",
                "test_location": test_dir,
                "results": all_results
            }, f, indent=2, default=str)

        self.logger.info(f"Batch testing complete. Results saved to {test_dir}")
        return all_results

