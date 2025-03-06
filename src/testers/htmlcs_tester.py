"""
HTML_CodeSniffer accessibility testing module
Uses HTML_CodeSniffer via Selenium for accessibility testing.
"""

import os
import json
from datetime import datetime
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from jinja2 import Template

from ..core.base_tester import BaseAccessibilityTester


class HTMLCSAccessibilityTester(BaseAccessibilityTester):
    """Accessibility tester using HTML_CodeSniffer."""

    def __init__(self, standard="WCAG2AA"):
        super().__init__("htmlcs")
        self.standard = standard
        self.logger = logging.getLogger(self.__class__.__name__)
        self.driver = None
        self.htmlcs_script = self._load_htmlcs_script()

    def _load_htmlcs_script(self):
        """Load the HTML_CodeSniffer JavaScript."""
        try:
            # Path to HTML_CodeSniffer script
            script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'HTMLCS.js')

            # Check if the script exists
            if not os.path.isfile(script_path):
                self.logger.warning("HTML_CodeSniffer script not found. Will try to load it from CDN.")
                return None

            with open(script_path, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            self.logger.error(f"Error loading HTML_CodeSniffer script: {str(e)}")
            return None

    def _setup_driver(self):
        """Setup Chrome webdriver."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def test_accessibility(self, url, test_dir=None):
        """Implement abstract method from BaseAccessibilityTester"""
        try:
            self.driver = self._setup_driver()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Navigate to the URL
            self.driver.get(url)

            # Wait for page to fully load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            # Inject HTML_CodeSniffer script
            if self.htmlcs_script:
                self.driver.execute_script(self.htmlcs_script)
            else:
                # Load from CDN as fallback
                self.driver.execute_script("""
                    var script = document.createElement('script');
                    script.src = 'https://squizlabs.github.io/HTML_CodeSniffer/build/HTMLCS.js';
                    document.head.appendChild(script);
                """)
                # Wait for the script to load
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return typeof window.HTMLCS !== 'undefined'")
                )

            # Run HTML_CodeSniffer
            results_json = self.driver.execute_script(f"""
                var messages = [];

                // Set up callback
                window.HTMLCS_RUNNER = new function() {{
                    this.run = function(standard) {{
                        HTMLCS.process(standard, document);
                        var msgs = HTMLCS.getMessages();
                        return msgs;
                    }};
                }};

                // Run the tests
                var messages = HTMLCS_RUNNER.run('{self.standard}');

                // Format the results
                var results = [];
                for (var i = 0; i < messages.length; i++) {{
                    var msg = messages[i];

                    // Get element info
                    var elementInfo = "";
                    if (msg.element) {{
                        elementInfo = msg.element.nodeName.toLowerCase();
                        if (msg.element.id) {{
                            elementInfo += "#" + msg.element.id;
                        }} else if (msg.element.className) {{
                            elementInfo += "." + msg.element.className.replace(/\\s+/g, ".");
                        }}
                    }}

                    results.push({{
                        type: msg.type,
                        code: msg.code,
                        msg: msg.msg,
                        technique: msg.code.split('.').slice(0, 3).join('.'),
                        element: elementInfo,
                        position: {{
                            x: msg.element ? msg.element.getBoundingClientRect().left : 0,
                            y: msg.element ? msg.element.getBoundingClientRect().top : 0
                        }},
                        elementHTML: msg.element ? msg.element.outerHTML.substring(0, 200) : ''
                    }});
                }}

                return JSON.stringify(results);
            """)

            # Parse JSON results
            messages = json.loads(results_json)

            # Format results
            results = {
                "tool": "htmlcs",
                "url": url,
                "timestamp": timestamp,
                "standard": self.standard,
                "messages": messages,
                "summary": {
                    "total": len(messages),
                    "errors": len([m for m in messages if m['type'] == 3]),
                    "warnings": len([m for m in messages if m['type'] == 2]),
                    "notices": len([m for m in messages if m['type'] == 1])
                },
                "test_dir": test_dir
            }

            return results

        except Exception as e:
            error_message = f"Error running HTML_CodeSniffer: {str(e)}"
            self.logger.error(error_message)
            return {
                "tool": "htmlcs",
                "url": url,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "error": error_message,
                "test_dir": test_dir
            }

        finally:
            if self.driver:
                self.driver.quit()

    def generate_report(self, results, output_dir):
        """Implement abstract method from BaseAccessibilityTester"""
        try:
            # Generate filenames
            page_id = results['url'].replace('https://', '').replace('http://', '').replace('/', '_')
            json_filename = f"htmlcs_{page_id}_{results['timestamp']}.json"
            html_filename = f"htmlcs_{page_id}_{results['timestamp']}.html"

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
        """Generate HTML report from HTML_CodeSniffer results."""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>HTML_CodeSniffer Accessibility Report</title>
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

                .code {
                    display: inline-block;
                    background-color: #f3f4f6;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: monospace;
                }

                .html-context {
                    background-color: #f9f9f9;
                    padding: 10px;
                    margin-top: 10px;
                    border-radius: 3px;
                    font-family: monospace;
                    overflow-x: auto;
                    white-space: pre-wrap;
                }

                .technique {
                    margin-top: 5px;
                    font-size: 14px;
                }

                .filter-options {
                    margin: 20px 0;
                    display: flex;
                    gap: 15px;
                }

                .filter-btn {
                    padding: 8px 15px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                }
                .filter-all { background-color: #e5e7eb; color: #374151; }
                .filter-errors { background-color: #fee2e2; color: #dc2626; }
                .filter-warnings { background-color: #fef3c7; color: #d97706; }
                .filter-notices { background-color: #dbeafe; color: #2563eb; }

                .filter-btn.active {
                    outline: 3px solid #6366f1;
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
                <h1>HTML_CodeSniffer Accessibility Report</h1>
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
            {% elif results.messages %}
                <h2>Accessibility Issues ({{ results.messages|length }})</h2>

                <div class="filter-options">
                    <button class="filter-btn filter-all active" onclick="filterIssues('all')">All ({{ results.messages|length }})</button>
                    <button class="filter-btn filter-errors" onclick="filterIssues('error')">Errors ({{ results.summary.errors }})</button>
                    <button class="filter-btn filter-warnings" onclick="filterIssues('warning')">Warnings ({{ results.summary.warnings }})</button>
                    <button class="filter-btn filter-notices" onclick="filterIssues('notice')">Notices ({{ results.summary.notices }})</button>
                </div>

                {% for message in results.messages %}
                    {% set type_class = 'error' if message.type == 3 else ('warning' if message.type == 2 else 'notice') %}
                    {% set type_name = 'Error' if message.type == 3 else ('Warning' if message.type == 2 else 'Notice') %}

                    <div class="issue issue-{{ type_class }} issue-type-{{ type_class }}">
                        <div class="issue-header">
                            <h3>{{ message.msg }}</h3>
                            <span class="issue-type type-{{ type_class }}">{{ type_name }}</span>
                        </div>

                        <p class="code">{{ message.code }}</p>

                        {% if message.technique %}
                            <p class="technique">Technique: {{ message.technique }}</p>
                        {% endif %}

                        {% if message.element %}
                            <p>Element: <code>{{ message.element }}</code></p>
                        {% endif %}

                        {% if message.elementHTML %}
                            <div class="html-context">{{ message.elementHTML }}</div>
                        {% endif %}
                    </div>
                {% endfor %}

                <script>
                    function filterIssues(type) {
                        // Update active button
                        const buttons = document.querySelectorAll('.filter-btn');
                        buttons.forEach(btn => btn.classList.remove('active'));
                        document.querySelector('.filter-' + (type === 'error' ? 'errors' : (type === 'warning' ? 'warnings' : (type === 'notice' ? 'notices' : 'all')))).classList.add('active');

                        // Filter issues
                        const issues = document.querySelectorAll('.issue');
                        issues.forEach(issue => {
                            if (type === 'all') {
                                issue.style.display = 'block';
                            } else {
                                issue.style.display = issue.classList.contains('issue-' + type) ? 'block' : 'none';
                            }
                        });
                    }
                </script>
            {% else %}
                <div class="no-issues">
                    <h2>No accessibility issues found!</h2>
                    <p>Congratulations! HTML_CodeSniffer did not detect any accessibility issues on this page.</p>
                </div>
            {% endif %}
        </body>
        </html>
        """

        return Template(template_str).render(results=results)