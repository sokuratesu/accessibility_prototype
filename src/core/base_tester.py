"""
Base tester module
Defines the abstract base class for all accessibility testers.
"""

from abc import ABC, abstractmethod
import logging


class BaseAccessibilityTester(ABC):
    """Abstract base class for accessibility testers."""

    def __init__(self, name):
        """Initialize the tester.

        Args:
            name (str): The name of the tester
        """
        self.name = name
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    @abstractmethod
    def test_accessibility(self, url, test_dir=None):
        """Run accessibility tests on the given URL.

        Args:
            url (str): The URL to test
            test_dir (str, optional): Directory to save test results

        Returns:
            dict: Test results
        """
        pass

    @abstractmethod
    def generate_report(self, results, output_dir):
        """Generate a report from test results.

        Args:
            results (dict): Test results from test_accessibility
            output_dir (str): Directory to save reports

        Returns:
            dict: Paths to generated reports
        """
        pass