"""
Parallel testing implementation for running tests on multiple browsers simultaneously.
"""

import os
import logging
import time
import concurrent.futures
from typing import List, Dict, Any, Callable, Tuple
from functools import partial


class ParallelTestRunner:
    """Run tests in parallel across multiple browsers and screen sizes."""

    def __init__(self, max_workers=None):
        """Initialize the parallel test runner.

        Args:
            max_workers (int, optional): Maximum number of worker threads
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_workers = max_workers

    def run_parallel_tests(self, test_function: Callable, test_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run tests in parallel.

        Args:
            test_function (callable): Function to run the test
            test_configs (list): List of test configurations

        Returns:
            list: Test results
        """
        results = []

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tests
                future_to_config = {
                    executor.submit(test_function, **config): config
                    for config in test_configs
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_config):
                    config = future_to_config[future]

                    try:
                        result = future.result()
                        results.append({
                            "config": config,
                            "result": result,
                            "status": "completed"
                        })
                        self.logger.info(
                            f"Completed test: {config.get('browser', 'Unknown')} - {config.get('screen_size', 'Unknown')}")

                    except Exception as e:
                        results.append({
                            "config": config,
                            "error": str(e),
                            "status": "failed"
                        })
                        self.logger.error(
                            f"Test failed: {config.get('browser', 'Unknown')} - {config.get('screen_size', 'Unknown')} - {str(e)}")

        except Exception as e:
            self.logger.error(f"Error in parallel test execution: {str(e)}")

        return results

    def run_browser_tests_in_parallel(self,
                                      url: str,
                                      testers: List[str],
                                      browsers: List[str],
                                      screen_sizes: List[Tuple[str, int, int]],
                                      test_function: Callable,
                                      test_dir: str,
                                      w3c_subtests: List[str] = None) -> Dict[str, Any]:
        """Run browser tests in parallel.

        Args:
            url (str): URL to test
            testers (list): List of tester IDs
            browsers (list): List of browser names
            screen_sizes (list): List of screen sizes (name, width, height)
            test_function (callable): Function to run the test
            test_dir (str): Directory to save results
            w3c_subtests (list, optional): W3C subtests to run

        Returns:
            dict: Test results
        """
        # Create test directory if needed
        os.makedirs(test_dir, exist_ok=True)

        # Create test configurations
        test_configs = []

        for browser in browsers:
            for size_name, width, height in screen_sizes:
                size_key = f"{size_name}_{width}x{height}"
                browser_dir = os.path.join(test_dir, browser)
                size_dir = os.path.join(browser_dir, size_key)

                test_configs.append({
                    "url": url,
                    "browser": browser,
                    "screen_size": (size_name, width, height),
                    "testers": testers,
                    "output_dir": size_dir,
                    "w3c_subtests": w3c_subtests
                })

        # Run tests in parallel
        test_results = self.run_parallel_tests(test_function, test_configs)

        # Organize results
        results = {
            "url": url,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "browsers": {}
        }

        for test_result in test_results:
            config = test_result["config"]
            browser = config["browser"]
            screen_size = config["screen_size"]
            size_key = f"{screen_size[0]}_{screen_size[1]}x{screen_size[2]}"

            if browser not in results["browsers"]:
                results["browsers"][browser] = {"screen_sizes": {}}

            if test_result["status"] == "completed":
                results["browsers"][browser]["screen_sizes"][size_key] = test_result["result"]
            else:
                results["browsers"][browser]["screen_sizes"][size_key] = {
                    "error": test_result.get("error", "Unknown error")
                }

        return results