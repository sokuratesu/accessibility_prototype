import os
import json
from datetime import datetime
import logging
import requests
from jinja2 import Template

from ..core.base_tester import BaseAccessibilityTester


class WaveAccessibilityTester(BaseAccessibilityTester):
    """Accessibility tester using WAVE API."""

    def __init__(self, api_key):
        super().__init__("wave")
        self.api_key = api_key
        self.timestamp = None

    def test_accessibility(self, url, test_dir=None):
        """Run WAVE accessibility test on the given URL."""
        try:
            self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # WAVE API endpoint
            wave_endpoint = f"https://wave.webaim.org/api/request"
            params = {
                "key": self.api_key,
                "url": url,
                "format": "json"
            }

            response = requests.get(wave_endpoint, params=params)
            response.raise_for_status()
            results = response.json()

            # Add metadata
            results.update({
                "tool": "wave",
                "url": url,
                "timestamp": self.timestamp
            })

            return results

        except Exception as e:
            self.logger.error(f"WAVE API error: {str(e)}")
            return {
                "tool": "wave",
                "url": url,
                "timestamp": self.timestamp,
                "error": str(e)
            }

    def generate_report(self, results, output_dir):
        """Generate report from WAVE results."""
        try:
            # Generate filenames
            page_id = results['url'].replace('https://', '').replace('http://', '').replace('/', '_')
            json_filename = f"wave_{page_id}_{results['timestamp']}.json"
            html_filename = f"wave_{page_id}_{results['timestamp']}.html"

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
        """Generate HTML report for WAVE results."""
        template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>WAVE Accessibility Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .error { color: red; }
                .warning { color: orange; }
                .success { color: green; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .summary { background-color: #f8f8f8; padding: 15px; margin-bottom: 20px; }
                h1, h2, h3 { color: #333; }
                .category { margin-top: 30px; }
                .issue-item { margin-bottom: 10px; border-left: 3px solid #ddd; padding-left: 10px; }
            </style>
        </head>
        <body>
            <h1>WAVE Accessibility Report</h1>
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>URL:</strong> {{ results.url }}</p>
                <p><strong>Date:</strong> {{ results.timestamp }}</p>
                <p><strong>WAVE Version:</strong> {{ results.statistics.version }}</p>
            </div>

            <div class="statistics">
                <h2>Statistics</h2>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                    </tr>
                    <tr class="error">
                        <td>Errors</td>
                        <td>{{ results.categories.error.count }}</td>
                    </tr>
                    <tr class="warning">
                        <td>Alerts</td>
                        <td>{{ results.categories.alert.count }}</td>
                    </tr>
                    <tr>
                        <td>Features</td>
                        <td>{{ results.categories.feature.count }}</td>
                    </tr>
                    <tr>
                        <td>Structure Elements</td>
                        <td>{{ results.categories.structure.count }}</td>
                    </tr>
                    <tr>
                        <td>HTML5 and ARIA</td>
                        <td>{{ results.categories.html5.count }}</td>
                    </tr>
                    <tr class="warning">
                        <td>Contrast Errors</td>
                        <td>{{ results.categories.contrast.count }}</td>
                    </tr>
                </table>
            </div>

            {% if results.categories.error.items %}
            <div class="category error">
                <h2>Errors</h2>
                {% for id, item in results.categories.error.items.items() %}
                <div class="issue-item">
                    <h3>{{ item.description }}</h3>
                    <p>Count: {{ item.count }}</p>
                    {% if item.help %}
                    <p><em>{{ item.help }}</em></p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if results.categories.alert.items %}
            <div class="category warning">
                <h2>Alerts</h2>
                {% for id, item in results.categories.alert.items.items() %}
                <div class="issue-item">
                    <h3>{{ item.description }}</h3>
                    <p>Count: {{ item.count }}</p>
                    {% if item.help %}
                    <p><em>{{ item.help }}</em></p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if results.categories.contrast.items %}
            <div class="category warning">
                <h2>Contrast Issues</h2>
                {% for id, item in results.categories.contrast.items.items() %}
                <div class="issue-item">
                    <h3>{{ item.description }}</h3>
                    <p>Count: {{ item.count }}</p>
                    {% if item.help %}
                    <p><em>{{ item.help }}</em></p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if results.categories.feature.items %}
            <div class="category success">
                <h2>Accessibility Features</h2>
                {% for id, item in results.categories.feature.items.items() %}
                <div class="issue-item">
                    <h3>{{ item.description }}</h3>
                    <p>Count: {{ item.count }}</p>
                    {% if item.help %}
                    <p><em>{{ item.help }}</em></p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </body>
        </html>
        """
        return Template(template).render(results=results)