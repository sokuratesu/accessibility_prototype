"""
Lighthouse accessibility testing module
Uses Google Lighthouse to perform accessibility audits.
"""

import os
import json
import tempfile
import subprocess
import shutil
import traceback
from datetime import datetime
import logging

from ..core.base_tester import BaseAccessibilityTester


class LighthouseAccessibilityTester(BaseAccessibilityTester):
    """Accessibility tester using Google Lighthouse."""

    def __init__(self):
        super().__init__("lighthouse")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._check_lighthouse_installation()

    def _check_lighthouse_installation(self):
        """Check if Lighthouse is installed."""
        try:
            result = subprocess.run(
                ["lighthouse", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
                shell=True,
            )
            if result.returncode != 0:
                self.logger.warning("Lighthouse not found. Make sure npm and Lighthouse are installed.")
                self.logger.warning("Install with: npm install -g lighthouse")
        except Exception as e:
            self.logger.warning(f"Error checking Lighthouse installation: {traceback.format_exc()}")

    def test_accessibility(self, url, test_dir=None):
        """Implement abstract method from BaseAccessibilityTester"""
        try:
            # Create a temporary directory to store Lighthouse report
            temp_dir = tempfile.mkdtemp()
            report_path = os.path.join(temp_dir, "lighthouse-report.json")

            # Run Lighthouse CLI with accessibility category only
            self.logger.info(f"Running Lighthouse on {url}")
            result = subprocess.run(
                [
                    "lighthouse",
                    url,
                    "--output=json",
                    "--output-path=" + report_path,
                    "--only-categories=accessibility",
                    "--chrome-flags=--headless --no-sandbox --disable-gpu"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            if result.returncode != 0:
                error_message = f"Lighthouse error: {result.stderr}"
                self.logger.error(error_message)
                return {
                    "tool": "lighthouse",
                    "url": url,
                    "timestamp": self.timestamp,
                    "error": error_message
                }

            # Read the JSON report
            with open(report_path, 'r', encoding='utf-8') as f:
                lighthouse_data = json.load(f)

            # Extract the relevant data
            accessibility_category = lighthouse_data.get("categories", {}).get("accessibility", {})
            accessibility_score = accessibility_category.get("score", 0)

            # Add metadata
            results = {
                "tool": "lighthouse",
                "url": url,
                "timestamp": self.timestamp,
                "accessibility_score": accessibility_score * 100,  # Convert to percentage
                "categories": lighthouse_data.get("categories", {}),
                "audits": {},
                "test_dir": test_dir
            }

            # Extract only accessibility audits
            for audit_id, audit in lighthouse_data.get("audits", {}).items():
                if any(ref.get("id") == "accessibility" for ref in audit.get("details", {}).get("items", [])):
                    results["audits"][audit_id] = audit

            # Clean up temp directory
            shutil.rmtree(temp_dir)

            return results

        except Exception as e:
            error_message = f"Error running Lighthouse: {traceback.format_exc()}"
            self.logger.error(error_message)
            return {
                "tool": "lighthouse",
                "url": url,
                "timestamp": self.timestamp,
                "error": error_message,
                "test_dir": test_dir
            }

    def generate_report(self, results, output_dir):
        """Implement abstract method from BaseAccessibilityTester"""
        try:
            # Generate filenames
            page_id = results['url'].replace('https://', '').replace('http://', '').replace('/', '_')
            json_filename = f"lighthouse_{page_id}_{results['timestamp']}.json"
            html_filename = f"lighthouse_{page_id}_{results['timestamp']}.html"

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
        """Generate HTML report from Lighthouse results."""
        from jinja2 import Template

        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lighthouse Accessibility Report</title>
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
                .score-container {
                    display: flex;
                    align-items: center;
                    margin: 20px 0;
                }
                .score-circle {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 32px;
                    font-weight: bold;
                    margin-right: 20px;
                }
                .score-good { background-color: #0cce6b; color: white; }
                .score-average { background-color: #ffa400; color: white; }
                .score-poor { background-color: #ff4e42; color: white; }
                .audit-card {
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 15px;
                }
                .audit-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .audit-title {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .audit-score {
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-weight: bold;
                }
                .audit-details {
                    margin-top: 10px;
                    background-color: #f9f9f9;
                    padding: 10px;
                    border-radius: 5px;
                }
                .passed { background-color: #d1fae5; color: #059669; }
                .failed { background-color: #fee2e2; color: #dc2626; }
                .na { background-color: #f3f4f6; color: #6b7280; }
                table {
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 10px;
                }
                th, td {
                    text-align: left;
                    padding: 8px;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
            <header>
                <h1>Lighthouse Accessibility Report</h1>
                <p><strong>URL:</strong> {{ results.url }}</p>
                <p><strong>Date:</strong> {{ results.timestamp }}</p>

                <div class="score-container">
                    {% set score = results.accessibility_score %}
                    <div class="score-circle {% if score >= 90 %}score-good{% elif score >= 50 %}score-average{% else %}score-poor{% endif %}">
                        {{ score|round }}%
                    </div>
                    <div>
                        <h2>Accessibility Score</h2>
                        <p>{{ results.categories.accessibility.description }}</p>
                    </div>
                </div>
            </header>

            {% if results.error %}
                <div class="audit-card failed">
                    <h2>Error</h2>
                    <p>{{ results.error }}</p>
                </div>
            {% else %}
                <h2>Accessibility Audits</h2>

                {% for audit_id, audit in results.audits.items() %}
                    <div class="audit-card">
                        <div class="audit-header">
                            <h3 class="audit-title">{{ audit.title }}</h3>
                            {% if audit.score is not none %}
                                <span class="audit-score {% if audit.score == 1 %}passed{% elif audit.score == 0 %}failed{% else %}na{% endif %}">
                                    {% if audit.score == 1 %}Pass{% elif audit.score == 0 %}Fail{% else %}N/A{% endif %}
                                </span>
                            {% endif %}
                        </div>

                        <p>{{ audit.description }}</p>

                        {% if audit.details %}
                            <details>
                                <summary>View Details</summary>
                                <div class="audit-details">
                                    {% if audit.details.items %}
                                        <table>
                                            <tr>
                                                {% for key in audit.details.headings %}
                                                    <th>{{ key.label if key.label else key.key }}</th>
                                                {% endfor %}
                                            </tr>
                                            {% for item in audit.details.items %}
                                                <tr>
                                                    {% for key in audit.details.headings %}
                                                        <td>{{ item[key.key]|string }}</td>
                                                    {% endfor %}
                                                </tr>
                                            {% endfor %}
                                        </table>
                                    {% else %}
                                        <pre>{{ audit.details|tojson(indent=2) }}</pre>
                                    {% endif %}
                                </div>
                            </details>
                        {% endif %}
                    </div>
                {% endfor %}
            {% endif %}
        </body>
        </html>
        """

        return Template(template_str).render(results=results)