"""
Test orchestrator module
Manages multiple accessibility tests and coordinates their execution.
"""

import os
import logging
import json
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
        results = {"tools": {}}
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
                results["tools"][tester_id] = test_result

            except Exception as e:
                error_message = f"Error running {tester_id}: {str(e)}"
                self.logger.error(error_message)
                results["tools"][tester_id] = {
                    "tool": tester_id,
                    "url": url,
                    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "error": error_message,
                    "test_dir": test_dir
                }

        # Save all results
        all_results_path = os.path.join(test_dir, "all_results.json")
        with open(all_results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        return results

