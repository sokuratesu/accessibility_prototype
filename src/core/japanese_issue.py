"""
Japanese accessibility issue class.
Represents an accessibility issue specific to Japanese language requirements.
"""


class JapaneseAccessibilityIssue:
    """Represents a Japanese-specific accessibility issue."""

    def __init__(self, check_type, element=None, issue_type=None, description=None):
        """Initialize a Japanese accessibility issue.

        Args:
            check_type (str): Type of check (e.g., 'encoding', 'typography')
            element (WebElement, optional): The element with the issue
            issue_type (str, optional): Type of issue
            description (str, optional): Description of the issue
        """
        self.check_type = check_type
        self.element = element
        self.issue_type = issue_type
        self.description = description
        self.element_path = None
        self.info = {}
        self.compliance = {}

    def set_path(self, path):
        """Set the element path.

        Args:
            path (str): Element path
        """
        self.element_path = path

    def add_info(self, key, value):
        """Add additional information.

        Args:
            key (str): Information key
            value: Information value
        """
        self.info[key] = value

    def set_compliance_info(self, compliance):
        """Set compliance information.

        Args:
            compliance (dict): Compliance information
        """
        self.compliance = compliance

    def to_dict(self):
        """Convert to dictionary.

        Returns:
            dict: Dictionary representation
        """
        return {
            "check_type": self.check_type,
            "issue_type": self.issue_type,
            "description": self.description,
            "element_path": self.element_path,
            "info": self.info,
            "compliance": self.compliance
        }