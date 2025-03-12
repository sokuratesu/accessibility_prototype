"""
W3C tools integration module
Integrates additional W3C accessibility testing tools.
"""

import os
import json
import logging
import tempfile
import time
import subprocess
from datetime import datetime
from urllib.parse import urlparse, quote_plus

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from jinja2 import Template

from ..core.base_tester import BaseAccessibilityTester


class W3CTester(BaseAccessibilityTester):
    """Accessibility tester using additional W3C tools."""

    def __init__(self):
        super().__init__("w3c_tools")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.driver = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Add this line to store enabled tests
        self.enabled_tests = None

        # Create lib directory if it doesn't exist
        lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'w3c_tools')
        os.makedirs(lib_dir, exist_ok=True)

        # Path to JS scripts
        self.scripts_dir = lib_dir

        # Check if required scripts exist
        self._check_required_files()

    def _check_required_files(self):
        """Check if required scripts and tools are available."""
        # Create aria validator script if it doesn't exist
        aria_validator_path = os.path.join(self.scripts_dir, "aria-validator.js")
        if not os.path.exists(aria_validator_path):
            self._create_aria_validator_script(aria_validator_path)

        # Check for vnu.jar
        vnu_path = os.path.join(self.scripts_dir, "vnu.jar")
        if not os.path.exists(vnu_path):
            self.logger.warning(f"vnu.jar not found in {vnu_path}.")
            self.logger.warning(
                "Download from https://validator.github.io/validator/ and place in the data/w3c_tools directory")

    def _create_aria_validator_script(self, path):
        """Create ARIA validator JavaScript file."""
        script_content = """
// ARIA Validator JavaScript
function validateARIA() {
    const allElements = document.querySelectorAll('*');
    const issues = [];

    const ariaRoles = [
        'alert', 'alertdialog', 'application', 'article', 'banner', 'button', 'cell', 'checkbox', 
        'columnheader', 'combobox', 'complementary', 'contentinfo', 'definition', 'dialog', 
        'directory', 'document', 'feed', 'figure', 'form', 'grid', 'gridcell', 'group', 'heading', 
        'img', 'link', 'list', 'listbox', 'listitem', 'log', 'main', 'marquee', 'math', 'menu', 
        'menubar', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'navigation', 'none', 'note', 
        'option', 'presentation', 'progressbar', 'radio', 'radiogroup', 'region', 'row', 'rowgroup', 
        'rowheader', 'scrollbar', 'search', 'searchbox', 'separator', 'slider', 'spinbutton', 
        'status', 'switch', 'tab', 'table', 'tablist', 'tabpanel', 'term', 'textbox', 'timer', 
        'toolbar', 'tooltip', 'tree', 'treegrid', 'treeitem'
    ];

    allElements.forEach(el => {
        // Check for invalid ARIA roles
        const role = el.getAttribute('role');
        if (role && !ariaRoles.includes(role)) {
            issues.push({
                element: el.tagName,
                id: el.id,
                class: el.className,
                issue: `Invalid ARIA role: ${role}`,
                severity: 'serious',
                wcag: 'ARIA4'
            });
        }

        // Check for ARIA attributes on elements that don't support them
        const hasAriaAttrs = Array.from(el.attributes).some(attr => attr.name.startsWith('aria-'));
        if (hasAriaAttrs && ['meta', 'br', 'style', 'script'].includes(el.tagName.toLowerCase())) {
            issues.push({
                element: el.tagName,
                id: el.id,
                class: el.className,
                issue: `ARIA attributes used on element that does not support them`,
                severity: 'critical',
                wcag: 'ARIA2'
            });
        }

        // Check for required ARIA attributes based on role
        if (role === 'checkbox' || role === 'radio') {
            if (!el.hasAttribute('aria-checked')) {
                issues.push({
                    element: el.tagName,
                    id: el.id,
                    class: el.className,
                    issue: `Missing required aria-checked attribute for ${role}`,
                    severity: 'serious',
                    wcag: 'ARIA8'
                });
            }
        }

        // Check for proper aria-labelledby references
        const labelledby = el.getAttribute('aria-labelledby');
        if (labelledby) {
            const ids = labelledby.split(/\\s+/);
            ids.forEach(id => {
                if (!document.getElementById(id)) {
                    issues.push({
                        element: el.tagName,
                        id: el.id,
                        class: el.className,
                        issue: `aria-labelledby references non-existent ID: ${id}`,
                        severity: 'critical',
                        wcag: 'ARIA16'
                    });
                }
            });
        }

        // Check for proper use of ARIA in focusable elements
        if (el.hasAttribute('tabindex') && parseInt(el.getAttribute('tabindex')) >= 0) {
            if (role === 'presentation' || role === 'none') {
                issues.push({
                    element: el.tagName,
                    id: el.id,
                    class: el.className,
                    issue: `Focusable element with presentation/none role`,
                    severity: 'serious',
                    wcag: 'ARIA6'
                });
            }
        }

        // Check for ARIA attributes that require specific roles
        if (el.hasAttribute('aria-pressed') && (role !== 'button')) {
            issues.push({
                element: el.tagName,
                id: el.id,
                class: el.className,
                issue: `aria-pressed used on element without button role`,
                severity: 'moderate',
                wcag: 'ARIA8'
            });
        }

        // Check for ARIA 1.1 features
        if (el.hasAttribute('aria-errormessage')) {
            const errorId = el.getAttribute('aria-errormessage');
            const errorElement = document.getElementById(errorId);
            if (errorElement && !errorElement.hasAttribute('aria-live')) {
                issues.push({
                    element: el.tagName,
                    id: el.id,
                    class: el.className,
                    issue: `Element referenced by aria-errormessage should have aria-live attribute`,
                    severity: 'moderate',
                    wcag: 'ARIA19'
                });
            }
        }
    });

    return {
        issues: issues,
        count: issues.length
    };
}

return validateARIA();
"""

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            self.logger.info(f"Created ARIA validator script at {path}")
        except Exception as e:
            self.logger.error(f"Error creating ARIA validator script: {str(e)}")

    def _setup_driver(self):
        """Setup webdriver for browser-based tests."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_size(1366, 768)  # Standard desktop size
        return driver

    def test_accessibility(self, url, test_dir=None, enabled_tests=None):
        """Run accessibility test on the given URL."""
        try:
            if test_dir:
                self.output_dir = test_dir
            else:
                self.output_dir = os.path.join(os.getcwd(), "Reports", f"w3c_test_{self.timestamp}")
                os.makedirs(self.output_dir, exist_ok=True)

            self.driver = self._setup_driver()

            results = {
                "tool": "w3c_tools",
                "url": url,
                "timestamp": self.timestamp,
                "test_dir": self.output_dir,
                "tests": {}
            }

            # Use self.enabled_tests to determine which tests to run
            enabled_tests = self.enabled_tests

            # If no specific tests are enabled, run all tests
            if enabled_tests is None:
                enabled_tests = ["html_validator", "css_validator", "link_checker",
                                 "nu_validator", "aria_validator", "dom_accessibility"]

            # Run HTML Validator
            if "html_validator" in enabled_tests:
                try:
                    results["tests"]["html_validator"] = self._run_html_validator(url)
                except Exception as e:
                    self.logger.error(f"HTML Validator error: {str(e)}")
                    results["tests"]["html_validator"] = {"error": str(e)}

            # Run CSS Validator
            if "css_validator" in enabled_tests:
                try:
                    results["tests"]["css_validator"] = self._run_css_validator(url)
                except Exception as e:
                    self.logger.error(f"CSS Validator error: {str(e)}")
                    results["tests"]["css_validator"] = {"error": str(e)}

            # Run Link Checker
            if "link_checker" in enabled_tests:
                try:
                    results["tests"]["link_checker"] = self._run_link_checker(url)
                except Exception as e:
                    self.logger.error(f"Link Checker error: {str(e)}")
                    results["tests"]["link_checker"] = {"error": str(e)}

            # Run Nu HTML Checker (if available)
            if "nu_validator" in enabled_tests:
                try:
                    results["tests"]["nu_validator"] = self._run_vnu_validator(url)
                except Exception as e:
                    self.logger.error(f"Nu HTML Checker error: {str(e)}")
                    results["tests"]["nu_validator"] = {"error": str(e)}

            # Run ARIA Validator
            if "aria_validator" in enabled_tests:
                try:
                    self.driver.get(url)
                    time.sleep(3)  # Allow page to load
                    results["tests"]["aria_validator"] = self._run_aria_validator()
                except Exception as e:
                    self.logger.error(f"ARIA Validator error: {str(e)}")
                    results["tests"]["aria_validator"] = {"error": str(e)}

            # Run DOMAccessibility Test
            if "dom_accessibility" in enabled_tests:
                try:
                    results["tests"]["dom_accessibility"] = self._run_dom_accessibility_test()
                except Exception as e:
                    self.logger.error(f"DOM Accessibility error: {str(e)}")
                    results["tests"]["dom_accessibility"] = {"error": str(e)}

            # Add summary results
            results["summary"] = self._create_summary(results["tests"])

            return results

        except Exception as e:
            error_message = f"Error running W3C tools: {str(e)}"
            self.logger.error(error_message)
            return {
                "tool": "w3c_tools",
                "url": url,
                "timestamp": self.timestamp,
                "error": error_message,
                "test_dir": self.output_dir if hasattr(self, 'output_dir') else test_dir
            }
        finally:
            if self.driver:
                self.driver.quit()

    def _run_html_validator(self, url):
        """Run W3C HTML Validator."""
        self.logger.info(f"Running HTML Validator on {url}")

        # W3C Validator API endpoint
        validator_url = f"https://validator.w3.org/nu/?doc={quote_plus(url)}&out=json"

        headers = {
            'User-Agent': 'Accessibility Testing Tool (https://github.com/yourusername/accessibility-tester)',
            'Accept': 'application/json'
        }

        response = requests.get(validator_url, headers=headers)
        results = response.json()

        # Process results
        messages = results.get("messages", [])

        categories = {
            "error": 0,
            "warning": 0,
            "info": 0
        }

        # Categorize issues
        for message in messages:
            msg_type = message.get("type", "info")
            if msg_type in categories:
                categories[msg_type] += 1

        validator_results = {
            "tool": "W3C HTML Validator",
            "issues": messages,
            "issue_count": len(messages),
            "categories": categories
        }

        return validator_results

    def _run_css_validator(self, url):
        """Run W3C CSS Validator."""
        self.logger.info(f"Running CSS Validator on {url}")

        # W3C CSS Validator API
        validator_url = f"https://jigsaw.w3.org/css-validator/validator?uri={quote_plus(url)}&profile=css3&output=json"

        response = requests.get(validator_url)

        try:
            results = response.json()
        except ValueError:
            # If response is not JSON, try to parse the error message
            soup = BeautifulSoup(response.text, 'html.parser')
            error_msg = soup.get_text()
            return {
                "tool": "W3C CSS Validator",
                "error": f"CSS Validator error: {error_msg[:200]}...",
                "issue_count": 0,
                "categories": {}
            }

        # Extract results from the response
        css_results = results.get("cssvalidation", {})
        errors = css_results.get("errors", [])
        warnings = css_results.get("warnings", [])

        validator_results = {
            "tool": "W3C CSS Validator",
            "errors": errors,
            "warnings": warnings,
            "issue_count": len(errors) + len(warnings),
            "categories": {
                "error": len(errors),
                "warning": len(warnings)
            }
        }

        return validator_results

    def _run_link_checker(self, url):
        """Run W3C Link Checker."""
        self.logger.info(f"Running Link Checker on {url}")

        # W3C Link Checker endpoint
        checker_url = f"https://validator.w3.org/checklink?uri={quote_plus(url)}&summary=on&hide_type=all&depth=3&check=Check"

        headers = {
            'User-Agent': 'Accessibility Testing Tool (https://github.com/yourusername/accessibility-tester)'
        }

        response = requests.get(checker_url, headers=headers)

        # Parse HTML response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract broken links
        broken_links = []
        for li in soup.select('li.msg_err'):
            link_text = li.get_text().strip()
            broken_links.append(link_text)

        # Extract redirected links
        redirected_links = []
        for li in soup.select('li.msg_info'):
            if "redirected" in li.get_text().lower():
                link_text = li.get_text().strip()
                redirected_links.append(link_text)

        checker_results = {
            "tool": "W3C Link Checker",
            "broken_links": broken_links,
            "redirected_links": redirected_links,
            "issue_count": len(broken_links),
            "categories": {
                "broken": len(broken_links),
                "redirected": len(redirected_links)
            }
        }

        return checker_results

    def _run_vnu_validator(self, url):
        """Run the Nu Html Checker (vnu.jar) for detailed HTML validation."""
        self.logger.info(f"Running Nu HTML Checker on {url}")

        # Check if vnu.jar exists
        vnu_path = os.path.join(self.scripts_dir, "vnu.jar")
        if not os.path.exists(vnu_path):
            return {
                "tool": "Nu HTML Checker",
                "error": f"vnu.jar not found in {vnu_path}. Please download it from https://validator.github.io/validator/",
                "issue_count": 0,
                "categories": {}
            }

        # Create temporary file for output
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            # Run vnu.jar on the URL
            cmd = [
                "java",
                "-jar",
                vnu_path,
                "--format", "json",
                url
            ]

            process = subprocess.run(cmd, capture_output=True, text=True)

            # Parse the output
            try:
                results = json.loads(process.stdout if process.stdout else process.stderr)
            except json.JSONDecodeError:
                # If both stdout and stderr fail to parse as JSON
                error_msg = process.stderr if process.stderr else "Unknown error"
                return {
                    "tool": "Nu HTML Checker",
                    "error": f"Failed to parse Nu HTML Checker output: {error_msg[:200]}...",
                    "issue_count": 0,
                    "categories": {}
                }

            # Process messages
            messages = results.get("messages", [])

            categories = {
                "error": 0,
                "warning": 0,
                "info": 0
            }

            # Categorize issues
            for message in messages:
                msg_type = message.get("type", "info")
                if msg_type in categories:
                    categories[msg_type] += 1

            vnu_results = {
                "tool": "Nu HTML Checker",
                "issues": messages,
                "issue_count": len(messages),
                "categories": categories
            }

            return vnu_results

        except Exception as e:
            return {
                "tool": "Nu HTML Checker",
                "error": f"Error running Nu HTML Checker: {str(e)}",
                "issue_count": 0,
                "categories": {}
            }
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def _run_aria_validator(self):
        """Run the ARIA Validator to check ARIA usage."""
        self.logger.info("Running ARIA Validator")

        # Load the ARIA validation script
        aria_script_path = os.path.join(self.scripts_dir, "aria-validator.js")

        if not os.path.exists(aria_script_path):
            return {
                "tool": "ARIA Validator",
                "error": f"ARIA validator script not found at {aria_script_path}",
                "issue_count": 0,
                "categories": {}
            }

        with open(aria_script_path, "r", encoding="utf-8") as f:
            aria_script = f.read()

        # Run the ARIA validation
        results = self.driver.execute_script(aria_script)

        # Process issues by severity
        categories = {
            "critical": 0,
            "serious": 0,
            "moderate": 0,
            "minor": 0
        }

        for issue in results.get("issues", []):
            severity = issue.get("severity", "moderate")
            if severity in categories:
                categories[severity] += 1

        aria_results = {
            "tool": "ARIA Validator",
            "issues": results.get("issues", []),
            "issue_count": results.get("count", 0),
            "categories": categories
        }

        return aria_results

    def _run_dom_accessibility_test(self):
        """Run DOM-based accessibility checks."""
        self.logger.info("Running DOM Accessibility Tests")

        script = """
        function testDOMAccessibility() {
            const issues = [];

            // Check for heading structure
            const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));

            // Sort headings by position in document
            headings.sort((a, b) => {
                const posA = a.getBoundingClientRect();
                const posB = b.getBoundingClientRect();
                return posA.top - posB.top;
            });

            // Check heading levels
            let prevLevel = 0;
            headings.forEach(heading => {
                const level = parseInt(heading.tagName.substring(1));

                // Check for skipped heading levels
                if (prevLevel > 0 && level > prevLevel + 1) {
                    issues.push({
                        element: heading.tagName,
                        text: heading.textContent.substring(0, 50),
                        issue: `Skipped heading level: h${prevLevel} to h${level}`,
                        severity: 'serious',
                        wcag: '2.4.6'
                    });
                }

                // Update previous level
                prevLevel = level;
            });

            // Check for focus order issues
            const focusableElements = document.querySelectorAll('a[href], button, input, textarea, select, [tabindex]');
            const elements = Array.from(focusableElements);

            // Check for negative tabindex
            elements.forEach(el => {
                const tabindex = el.getAttribute('tabindex');
                if (tabindex && parseInt(tabindex) < 0) {
                    issues.push({
                        element: el.tagName,
                        id: el.id,
                        class: el.className,
                        issue: 'Element with negative tabindex will be excluded from keyboard navigation',
                        severity: 'moderate',
                        wcag: '2.1.1'
                    });
                }
            });

            // Check for visible focus styles (WCAG 2.4.7)
            document.querySelectorAll('a, button, [role="button"], [tabindex]').forEach(el => {
                const computedStyle = window.getComputedStyle(el);
                const hasVisibleFocus = (
                    computedStyle.outlineStyle !== 'none' ||
                    computedStyle.boxShadow !== 'none' ||
                    computedStyle.borderStyle !== 'none'
                );

                if (!hasVisibleFocus) {
                    issues.push({
                        element: el.tagName,
                        id: el.id,
                        class: el.className,
                        issue: 'Element may not have visible focus indicator',
                        severity: 'moderate',
                        wcag: '2.4.7'
                    });
                }
            });

            // Check for landmark regions (WCAG 2.4.1)
            const landmarks = document.querySelectorAll('main, [role="main"], nav, [role="navigation"], aside, [role="complementary"]');
            if (landmarks.length === 0) {
                issues.push({
                    element: 'body',
                    issue: 'No landmark regions found (main, nav, aside)',
                    severity: 'moderate',
                    wcag: '2.4.1'
                });
            }

            // Check for page title (WCAG 2.4.2)
            if (!document.title || document.title.trim() === '') {
                issues.push({
                    element: 'title',
                    issue: 'Page title is empty or missing',
                    severity: 'serious',
                    wcag: '2.4.2'
                });
            }

            // Check for meta viewport restrictions (WCAG 1.4.4)
            const viewport = document.querySelector('meta[name="viewport"]');
            if (viewport) {
                const content = viewport.getAttribute('content') || '';
                if (content.includes('user-scalable=no') || content.includes('maximum-scale=1.0')) {
                    issues.push({
                        element: 'meta[name="viewport"]',
                        content: content,
                        issue: 'Viewport meta tag restricts zooming/scaling',
                        severity: 'serious',
                        wcag: '1.4.4'
                    });
                }
            }

            // Check for language attribute (WCAG 3.1.1)
            const html = document.querySelector('html');
            if (!html.hasAttribute('lang')) {
                issues.push({
                    element: 'html',
                    issue: 'Missing lang attribute on html element',
                    severity: 'serious',
                    wcag: '3.1.1'
                });
            }

            // Check for empty links or buttons
            document.querySelectorAll('a, button').forEach(el => {
                if (el.textContent.trim() === '' && el.querySelectorAll('img, svg, [aria-label]').length === 0 && !el.hasAttribute('aria-label')) {
                    issues.push({
                        element: el.tagName,
                        id: el.id,
                        class: el.className,
                        issue: 'Empty link or button without accessible name',
                        severity: 'serious',
                        wcag: '2.4.4'
                    });
                }
            });

            // Return the issues
            return {
                issues: issues,
                count: issues.length
            };
        }

        return testDOMAccessibility();
        """

        results = self.driver.execute_script(script)

        # Process issues by severity
        categories = {
            "critical": 0,
            "serious": 0,
            "moderate": 0,
            "minor": 0
        }

        for issue in results.get("issues", []):
            severity = issue.get("severity", "moderate")
            if severity in categories:
                categories[severity] += 1

        dom_results = {
            "tool": "DOM Accessibility",
            "issues": results.get("issues", []),
            "issue_count": results.get("count", 0),
            "categories": categories
        }

        return dom_results

    def _create_summary(self, tests):
        """Create a summary of all test results."""
        summary = {
            "total_issues": 0,
            "categories": {
                "critical": 0,
                "serious": 0,
                "moderate": 0,
                "minor": 0,
                "error": 0,
                "warning": 0,
                "info": 0
            }
        }

        # Sum up issues from all tests
        for test_name, test_results in tests.items():
            # Skip if there's an error
            if "error" in test_results:
                continue

            # Add to total issues
            summary["total_issues"] += test_results.get("issue_count", 0)

            # Add issues by category
            for category, count in test_results.get("categories", {}).items():
                if category in summary["categories"]:
                    summary["categories"][category] += count

        return summary

    def generate_report(self, results, output_dir):
        """Generate report from test results."""
        try:
            # Generate filenames
            page_id = results['url'].replace('https://', '').replace('http://', '').replace('/', '_')
            json_filename = f"w3c_tools_{page_id}_{results['timestamp']}.json"
            html_filename = f"w3c_tools_{page_id}_{results['timestamp']}.html"

            # Create directories
            os.makedirs(os.path.join(output_dir, "json_reports"), exist_ok=True)
            os.makedirs(os.path.join(output_dir, "html_reports"), exist_ok=True)

            # Save JSON report
            json_path = os.path.join(output_dir, "json_reports", json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            # Generate and save HTML report
            html_report = self._generate_html_report(results)
            html_path = os.path.join(output_dir, "html_reports", html_filename)
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
        """Generate HTML report from test results."""
        template_str = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>W3C Tools Accessibility Report</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }
            .container { max-width: 1200px; margin: 0 auto; }
            header { background-color: #f8f9fa; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
            h1, h2, h3 { color: #205493; }
            .summary-box { display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }
            .summary-item { flex: 1; min-width: 200px; padding: 15px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .critical { background-color: #f9dede; }
            .serious { background-color: #fff1d2; }
            .moderate { background-color: #e1f3f8; }
            .minor { background-color: #e7f4e4; }
            .error { background-color: #f9dede; }
            .warning { background-color: #fff1d2; }
            .info { background-color: #e1f3f8; }

            .test-section { margin-bottom: 30px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; }
            .test-header { padding: 15px; background-color: #f8f9fa; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; }
            .issues-container { padding: 15px; }
            .issue-item { margin-bottom: 10px; padding: 10px; border-left: 4px solid #ddd; }
            .issue-item.critical { border-left-color: #dc3545; }
            .issue-item.serious { border-left-color: #fd7e14; }
            .issue-item.moderate { border-left-color: #17a2b8; }
            .issue-item.minor { border-left-color: #28a745; }
            .issue-item.error { border-left-color: #dc3545; }
            .issue-item.warning { border-left-color: #fd7e14; }
            .issue-item.info { border-left-color: #17a2b8; }

            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 10px; text-align: left; border: 1px solid #ddd; }
            th { background-color: #f8f9fa; }

            details { margin-top: 10px; }
            summary { cursor: pointer; padding: 8px; background-color: #f8f9fa; }

            .error-message { padding: 15px; background-color: #f9dede; color: #721c24; border-radius: 5px; margin-bottom: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>W3C Tools Accessibility Report</h1>
                <p><strong>URL:</strong> {{ results.url }}</p>
                <p><strong>Date:</strong> {{ results.timestamp }}</p>
            </header>

            {% if results.error %}
                <div class="error-message">
                    <h2>Error</h2>
                    <p>{{ results.error }}</p>
                </div>
            {% else %}
                <section>
                    <h2>Summary</h2>
                    <div class="summary-box">
                        <div class="summary-item">
                            <h3>Total Issues</h3>
                            <p>{{ results.summary.total_issues }}</p>
                        </div>
                        {% for category, count in results.summary.categories.items() %}
                            {% if count > 0 %}
                                <div class="summary-item {{ category }}">
                                    <h3>{{ category|title }}</h3>
                                    <p>{{ count }}</p>
                                </div>
                            {% endif %}
                        {% endfor %}
                    </div>
                </section>

                {% for test_name, test_data in results.tests.items() %}
                    <section class="test-section">
                        <div class="test-header">
                            <h2>{{ test_data.tool }}</h2>
                            <span>{{ test_data.issue_count }} issue(s) found</span>
                        </div>

                        {% if test_data.error %}
                            <div class="error-message">
                                <p>{{ test_data.error }}</p>
                            </div>
                        {% else %}
                            <div class="issues-container">
                                {% if test_name == 'html_validator' or test_name == 'nu_validator' %}
                                    {% if test_data.issues %}
                                        <table>
                                            <tr>
                                                <th>Type</th>
                                                <th>Message</th>
                                                <th>Line</th>
                                                <th>Column</th>
                                            </tr>
                                            {% for issue in test_data.issues %}
                                                <tr class="{{ issue.type }}">
                                                    <td>{{ issue.type }}</td>
                                                    <td>{{ issue.message }}</td>
                                                    <td>{{ issue.line if issue.line else 'N/A' }}</td>
                                                    <td>{{ issue.column if issue.column else 'N/A' }}</td>
                                                </tr>
                                            {% endfor %}
                                        </table>
                                    {% else %}
                                        <p>No issues found</p>
                                    {% endif %}
                                {% elif test_name == 'css_validator' %}
                                    {% if test_data.errors %}
                                        <h3>Errors ({{ test_data.errors|length }})</h3>
                                        <table>
                                            <tr>
                                                <th>Line</th>
                                                <th>Message</th>
                                            </tr>
                                            {% for error in test_data.errors %}
                                                <tr>
                                                    <td>{{ error.line }}</td>
                                                    <td>{{ error.message }}</td>
                                                </tr>
                                            {% endfor %}
                                        </table>
                                    {% endif %}

                                    {% if test_data.warnings %}
                                        <h3>Warnings ({{ test_data.warnings|length }})</h3>
                                        <table>
                                            <tr>
                                                <th>Line</th>
                                                <th>Message</th>
                                            </tr>
                                            {% for warning in test_data.warnings %}
                                                <tr>
                                                    <td>{{ warning.line }}</td>
                                                    <td>{{ warning.message }}</td>
                                                </tr>
                                            {% endfor %}
                                        </table>
                                    {% endif %}

                                    {% if not test_data.errors and not test_data.warnings %}
                                        <p>No CSS issues found</p>
                                    {% endif %}
                                {% elif test_name == 'link_checker' %}
                                    {% if test_data.broken_links %}
                                        <h3>Broken Links ({{ test_data.broken_links|length }})</h3>
                                        <ul>
                                            {% for link in test_data.broken_links %}
                                                <li>{{ link }}</li>
                                            {% endfor %}
                                        </ul>
                                    {% endif %}

                                    {% if test_data.redirected_links %}
                                        <h3>Redirected Links ({{ test_data.redirected_links|length }})</h3>
                                        <ul>
                                            {% for link in test_data.redirected_links %}
                                                <li>{{ link }}</li>
                                            {% endfor %}
                                        </ul>
                                    {% endif %}

                                    {% if not test_data.broken_links and not test_data.redirected_links %}
                                        <p>No link issues found</p>
                                    {% endif %}
                                {% else %}
                                    {% if test_data.issues %}
                                        {% for issue in test_data.issues %}
                                            <div class="issue-item {{ issue.severity if issue.severity else 'minor' }}">
                                                <h4>{{ issue.issue }}</h4>
                                                {% if issue.element %}
                                                    <p><strong>Element:</strong> {{ issue.element }}</p>
                                                {% endif %}
                                                {% if issue.id %}
                                                    <p><strong>ID:</strong> {{ issue.id }}</p>
                                                {% endif %}
                                                {% if issue.class %}
                                                    <p><strong>Class:</strong> {{ issue.class }}</p>
                                                {% endif %}
                                                {% if issue.wcag %}
                                                    <p><strong>WCAG:</strong> {{ issue.wcag }}</p>
                                                {% endif %}
                                                {% if issue.severity %}
                                                    <p><strong>Severity:</strong> {{ issue.severity }}</p>
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    {% else %}
                                        <p>No issues found</p>
                                    {% endif %}
                                {% endif %}
                            </div>
                        {% endif %}
                    </section>
                {% endfor %}
            {% endif %}
        </div>
    </body>
    </html>
        """

        # Render the template with the results
        from jinja2 import Template
        return Template(template_str).render(results=results)