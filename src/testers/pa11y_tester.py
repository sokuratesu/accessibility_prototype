"""
Pa11y accessibility testing module
Uses Pa11y CLI to perform accessibility audits.
"""

import os
import json
import subprocess
import tempfile
import shutil
import traceback
from datetime import datetime
import logging

from ..core.base_tester import BaseAccessibilityTester


class Pa11yAccessibilityTester(BaseAccessibilityTester):
    """Accessibility tester using Pa11y."""

    def __init__(self, standard="WCAG2AA"):
        super().__init__("pa11y")
        self.standard = standard
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._check_pa11y_installation()

    def _check_pa11y_installation(self):
        """Check if Pa11y is installed."""
        try:
            result = subprocess.run(
                ["pa11y", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            if result.returncode != 0:
                self.logger.warning("Pa11y not found. Make sure npm and Pa11y are installed.")
                self.logger.warning("Install with: npm install -g pa11y")
        except Exception as e:
            self.logger.warning(f"Error checking Pa11y installation: {str(e)}")

    def test_accessibility(self, url, test_dir=None):
        """Implement abstract method from BaseAccessibilityTester"""
        try:
            # Create a temporary file to store Pa11y report
            temp_dir = tempfile.mkdtemp()
            report_path = os.path.join(temp_dir, "pa11y-report.json")

            # Run Pa11y CLI
            self.logger.info(f"Running Pa11y on {url}")
            cmd = [
                "pa11y",
                url,
                "--standard", self.standard,
                "--reporter", "json",
                "--include-notices",
                "--include-warnings",
                "--timeout", "60000"  # 60 seconds timeout
            ]

            with open(report_path, 'w') as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )

            if result.returncode != 0 and not os.path.exists(report_path):
                error_message = f"Pa11y error: {result.stderr}"
                self.logger.error(error_message)
                return {
                    "tool": "pa11y",
                    "url": url,
                    "timestamp": self.timestamp,
                    "error": error_message,
                    "test_dir": test_dir
                }

            # Read the JSON report
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    pa11y_data = json.load(f)
            except json.JSONDecodeError:
                # Handle case where Pa11y outputs an error in a non-JSON format
                with open(report_path, 'r', encoding='utf-8') as f:
                    error_content = f.read()
                return {
                    "tool": "pa11y",
                    "url": url,
                    "timestamp": self.timestamp,
                    "error": f"Failed to parse Pa11y output: {error_content}",
                    "test_dir": test_dir
                }

            # Add metadata
            results = {
                    "tool": "pa11y",
                    "url": url,
                    "timestamp": self.timestamp,
                    "standard": self.standard,
                    "issues": pa11y_data if isinstance(pa11y_data, list) else [],
                    "test_dir": test_dir,
                    "summary": {
                        "total": len(pa11y_data) if isinstance(pa11y_data, list) else 0,
                        "errors": len([i for i in pa11y_data if i.get("type") == "error"]) if isinstance(pa11y_data,
                                                                                                         list) else 0,
                        "warnings": len([i for i in pa11y_data if i.get("type") == "warning"]) if isinstance(pa11y_data,
                                                                                                             list) else 0,
                        "notices": len([i for i in pa11y_data if i.get("type") == "notice"]) if isinstance(pa11y_data,
                                                                                                           list) else 0
                    }
                }

            # Clean up temp directory
            shutil.rmtree(temp_dir)

            return results

        except Exception as e:
               error_message = f"Error running Pa11y: {traceback.format_exc()}"
               self.logger.error(error_message)
               return {
                   "tool": "pa11y",
                   "url": url,
                   "timestamp": self.timestamp,
                   "error": error_message,
                   "test_dir": test_dir
               }
        finally:
            pass

    def generate_report(self, results, output_dir):
                """Implement abstract method from BaseAccessibilityTester"""
                try:
                    # Generate filenames
                    page_id = results['url'].replace('https://', '').replace('http://', '').replace('/', '_')
                    json_filename = f"pa11y_{page_id}_{results['timestamp']}.json"
                    html_filename = f"pa11y_{page_id}_{results['timestamp']}.html"

                    # Save JSON report
                    json_path = os.path.join(output_dir, "json_reports", json_filename)
                    os.makedirs(os.path.dirname(json_path), exist_ok=True)
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2)

                    # Generate and save HTML report
                    html_report = self._generate_html_report(results)
                    html_path = os.path.join(output_dir, "html_reports", html_filename)
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

    def _generate_html_report(self, results):
        """Generate HTML report from Pa11y results."""
        from jinja2 import Template

        template_str = """
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>Pa11y Accessibility Report</title>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <style>
                                    body {
                                        font-family: Arial, sans-serif;
                                        line-height: 1.6;
                                        color: #333;
                                        max-width: 1200px;
                                        margin: 0 auto;
                                        padding: 20px;
                                    }
                                    header {
                                        background-color: #f5f5f5;
                                        padding: 20px;
                                        margin-bottom: 30px;
                                        border-radius: 5px;
                                    }
                                    .summary {
                                        display: flex;
                                        justify-content: space-between;
                                        max-width: 600px;
                                        margin: 20px 0;
                                    }
                                    .summary-item {
                                        text-align: center;
                                        padding: 10px;
                                        border-radius: 5px;
                                    }
                                    .error-summary { background-color: #fee2e2; color: #dc2626; }
                                    .warning-summary { background-color: #fef3c7; color: #d97706; }
                                    .notice-summary { background-color: #dbeafe; color: #2563eb; }
                                    .issue {
                                        border: 1px solid #ddd;
                                        border-radius: 5px;
                                        padding: 15px;
                                        margin-bottom: 15px;
                                    }
                                    .issue-error { border-left: 5px solid #dc2626; }
                                    .issue-warning { border-left: 5px solid #d97706; }
                                    .issue-notice { border-left: 5px solid #2563eb; }
                                    .issue-header {
                                        display: flex;
                                        justify-content: space-between;
                                        align-items: center;
                                    }
                                    .issue-type {
                                        padding: 3px 8px;
                                        border-radius: 12px;
                                        font-weight: bold;
                                        font-size: 14px;
                                    }
                                    .type-error { background-color: #fee2e2; color: #dc2626; }
                                    .type-warning { background-color: #fef3c7; color: #d97706; }
                                    .type-notice { background-color: #dbeafe; color: #2563eb; }
                                    .context {
                                        background-color: #f9f9f9;
                                        padding: 10px;
                                        margin-top: 10px;
                                        border-radius: 3px;
                                        font-family: monospace;
                                        overflow-x: auto;
                                    }
                                    .selector {
                                        margin-top: 10px;
                                        font-family: monospace;
                                        font-size: 14px;
                                        color: #6b7280;
                                    }
                                    .no-issues {
                                        padding: 20px;
                                        text-align: center;
                                        background-color: #d1fae5;
                                        color: #059669;
                                        border-radius: 5px;
                                        margin-top: 20px;
                                    }
                                    .error-message {
                                        padding: 20px;
                                        background-color: #fee2e2;
                                        color: #dc2626;
                                        border-radius: 5px;
                                        margin-top: 20px;
                                    }
                                </style>
                            </head>
                            <body>
                                <header>
                                    <h1>Pa11y Accessibility Report</h1>
                                    <p><strong>URL:</strong> {{ results.url }}</p>
                                    <p><strong>Date:</strong> {{ results.timestamp }}</p>
                                    <p><strong>Standard:</strong> {{ results.standard }}</p>

                                    {% if results.summary %}
                                    <div class="summary">
                                        <div class="summary-item error-summary">
                                            <h3>Errors</h3>
                                            <span>{{ results.summary.errors }}</span>
                                        </div>
                                        <div class="summary-item warning-summary">
                                            <h3>Warnings</h3>
                                            <span>{{ results.summary.warnings }}</span>
                                        </div>
                                        <div class="summary-item notice-summary">
                                            <h3>Notices</h3>
                                            <span>{{ results.summary.notices }}</span>
                                        </div>
                                    </div>
                                    {% endif %}
                                </header>

                                {% if results.error %}
                                    <div class="error-message">
                                        <h2>Error</h2>
                                        <p>{{ results.error }}</p>
                                    </div>
                                {% elif results.issues %}
                                    <h2>Accessibility Issues ({{ results.issues|length }})</h2>

                                    {% for issue in results.issues %}
                                        <div class="issue issue-{{ issue.type }}">
                                            <div class="issue-header">
                                                <h3>{{ issue.message }}</h3>
                                                <span class="issue-type type-{{ issue.type }}">{{ issue.type|capitalize }}</span>
                                            </div>

                                            {% if issue.code %}
                                                <p><strong>Code:</strong> {{ issue.code }}</p>
                                            {% endif %}

                                            {% if issue.context %}
                                                <div class="context">{{ issue.context }}</div>
                                            {% endif %}

                                            {% if issue.selector %}
                                                <div class="selector">{{ issue.selector }}</div>
                                            {% endif %}
                                        </div>
                                    {% endfor %}
                                {% else %}
                                    <div class="no-issues">
                                        <h2>No accessibility issues found!</h2>
                                        <p>Congratulations! Pa11y did not detect any accessibility issues on this page.</p>
                                    </div>
                                {% endif %}
                            </body>
                            </html>
                            """

        return Template(template_str).render(results=results)
