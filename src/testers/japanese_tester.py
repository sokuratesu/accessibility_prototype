"""
Japanese accessibility testing module
Provides specialized accessibility testing for Japanese websites.
"""

import os
import json
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from jinja2 import Template

from ..core.base_tester import BaseAccessibilityTester
from data.japanese_config import JAPANESE_CONFIG, JAPANESE_WCAG_MAPPING


class JapaneseAccessibilityIssue:
    """Class to represent a Japanese accessibility issue"""

    def __init__(self, check_type, element=None, issue_type="error", description=""):
        self.check_type = check_type
        self.element = element
        self.issue_type = issue_type
        self.description = description
        self.path = None
        self.compliance_info = None
        self.additional_info = {}

    def set_path(self, path):
        self.path = path
        return self

    def set_compliance_info(self, compliance_info):
        self.compliance_info = compliance_info
        return self

    def add_info(self, key, value):
        self.additional_info[key] = value
        return self

    def to_dict(self):
        return {
            'check_type': self.check_type,
            'issue_type': self.issue_type,
            'description': self.description,
            'element_path': self.path,
            'compliance': self.compliance_info,
            'details': self.additional_info
        }


class JapaneseAccessibilityTester(BaseAccessibilityTester):
    """Japanese accessibility testing implementation."""

    def __init__(self):
        super().__init__("japanese_a11y")
        self.config = JAPANESE_CONFIG
        self.form_zero_enabled = True
        self.driver = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _setup_driver(self):
        """Setup webdriver with Japanese-specific configurations."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Run in headless mode
            options.add_argument('--lang=ja')  # Set language to Japanese
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            # Add Japanese fonts
            options.add_argument('--font-render-hinting=none')

            # Set preferences for Japanese content
            options.add_experimental_option('prefs', {
                'intl.accept_languages': 'ja,ja_JP',
                'font.language_override': 'ja'
            })

            # Initialize the driver with ChromeDriverManager
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )

            # Set window size
            driver.set_window_size(1366, 768)

            # Set page load timeout
            driver.set_page_load_timeout(30)

            # Enable Japanese IME
            driver.execute_cdp_cmd('Page.enable', {})
            driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                'behavior': 'allow',
                'downloadPath': '.'
            })

            return driver

        except Exception as e:
            self.logger.error(f"Error setting up driver: {str(e)}")
            raise Exception(f"Failed to setup driver: {str(e)}")

    def test_accessibility(self, url, test_dir=None):
        """Implement abstract method from BaseAccessibilityTester"""
        try:
            print(f"Starting Japanese accessibility test for {url}")  # Debug print
            self.driver = self._setup_driver()
            print("Driver setup complete")  # Debug print

            self.driver.get(url)
            print("Page loaded successfully")  # Debug print

            results = {
                "tool": "japanese_a11y",
                "url": url,
                "timestamp": self.timestamp,
                "test_dir": test_dir,
                "results": {}
            }

            # Run each test with error handling
            try:
                results["results"]["encoding"] = self._check_encoding(url)
                print("Encoding check complete")  # Debug print
            except Exception as e:
                results["results"]["encoding"] = {"error": str(e)}

            try:
                results["results"]["typography"] = self._check_typography(self.driver)
                print("Typography check complete")  # Debug print
            except Exception as e:
                results["results"]["typography"] = {"error": str(e)}

            try:
                results["results"]["input_methods"] = self._check_input_methods(self.driver)
                print("Input methods check complete")  # Debug print
            except Exception as e:
                results["results"]["input_methods"] = {"error": str(e)}

            try:
                results["results"]["screen_reader"] = self._check_screen_reader_compatibility(self.driver)
                print("Screen reader compatibility check complete")  # Debug print
            except Exception as e:
                results["results"]["screen_reader"] = {"error": str(e)}

            try:
                results["results"]["text_resize"] = self._check_text_resize(self.driver)
                print("Text resize check complete")  # Debug print
            except Exception as e:
                results["results"]["text_resize"] = {"error": str(e)}

            try:
                results["results"]["color_contrast"] = self._check_color_contrast(self.driver)
                print("Color contrast check complete")  # Debug print
            except Exception as e:
                results["results"]["color_contrast"] = {"error": str(e)}

            try:
                results["results"]["ruby_text"] = self._check_ruby_text(url)
                print("Ruby text check complete")  # Debug print
            except Exception as e:
                results["results"]["ruby_text"] = {"error": str(e)}

            if self.form_zero_enabled:
                try:
                    results["results"]["form_zero"] = self._check_form_zero(url)
                    print("Form Zero check complete")  # Debug print
                except Exception as e:
                    results["results"]["form_zero"] = {"error": str(e)}

            print("All Japanese accessibility tests completed")  # Debug print
            return results

        except Exception as e:
            error_msg = f"Error in Japanese accessibility test: {str(e)}"
            print(error_msg)  # Debug print
            return {
                "tool": "japanese_a11y",
                "url": url,
                "timestamp": self.timestamp,
                "test_dir": test_dir,
                "error": error_msg
            }
        finally:
            if self.driver:
                self.driver.quit()
                print("Driver closed")  # Debug print

    def generate_report(self, results, output_dir):
        """Implement abstract method from BaseAccessibilityTester"""
        try:
            # Generate filenames
            page_id = results['url'].replace('https://', '').replace('http://', '').replace('/', '_')
            json_filename = f"japanese_a11y_{page_id}_{results['timestamp']}.json"
            html_filename = f"japanese_a11y_{page_id}_{results['timestamp']}.html"

            # Save JSON report
            json_path = os.path.join(output_dir, "json_reports", json_filename)
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

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
        """Generate HTML report for Japanese accessibility results"""
        template = """
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Japanese Accessibility Report</title>
            <style>
                body {
                    font-family: 'Meiryo', 'Hiragino Kaku Gothic Pro', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 20px;
                }
                h1, h2, h3, h4 {
                    color: #1a237e;
                }
                .test-section {
                    margin-bottom: 30px;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    background-color: #fff;
                }
                .test-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eee;
                }
                .issues-count {
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-size: 0.9em;
                    font-weight: bold;
                }
                .issues-count.high { background: #fee2e2; color: #dc2626; }
                .issues-count.medium { background: #fef3c7; color: #d97706; }
                .issues-count.low { background: #dbeafe; color: #2563eb; }
                .issues-count.none { background: #d1fae5; color: #059669; }
                .details-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }
                .details-table th, .details-table td {
                    padding: 8px;
                    border: 1px solid #ddd;
                    text-align: left;
                }
                .details-table th { background: #f8f9fa; }
                .recommendations {
                    margin-top: 20px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 5px;
                }
                .error-message {
                    color: #dc2626;
                    background: #fee2e2;
                    padding: 10px;
                    border-radius: 5px;
                }
                .summary {
                    background-color: #f8f9fa;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <h1>Japanese Accessibility Report</h1>
            <div class="summary">
                <h2>Basic Information</h2>
                <p><strong>URL:</strong> {{ results.url }}</p>
                <p><strong>Test Date:</strong> {{ results.timestamp }}</p>
            </div>

            {% if results.error %}
                <div class="error-message">
                    <h2>Error</h2>
                    <p>{{ results.error }}</p>
                </div>
            {% elif results.results %}
                {% for test_name, test_data in results.results.items() %}
                    <div class="test-section">
                        <div class="test-header">
                            <h2>{{ test_name|title }}</h2>
                            {% if test_data.issues_found is defined %}
                                <span class="issues-count {% if test_data.issues_found > 10 %}high{% elif test_data.issues_found > 5 %}medium{% elif test_data.issues_found > 0 %}low{% else %}none{% endif %}">
                                    Issues found: {{ test_data.issues_found }}
                                </span>
                            {% endif %}
                        </div>

                        {% if test_data.error %}
                            <p class="error-message">Error: {{ test_data.error }}</p>
                        {% else %}
                            {% if test_name == 'typography' %}
                                {% for type_name, type_data in test_data.items() %}
                                    <h3>{{ type_name|title }}</h3>
                                    {% if type_data.issues_found is defined %}
                                        <p>Issues found: {{ type_data.issues_found }}</p>
                                        {% if type_data.details %}
                                            <table class="details-table">
                                                <tr>
                                                    <th>Element</th>
                                                    <th>Text</th>
                                                    <th>Current</th>
                                                    <th>Required</th>
                                                </tr>
                                                {% for detail in type_data.details %}
                                                    <tr>
                                                        <td>{{ detail.element }}</td>
                                                        <td>{{ detail.text }}</td>
                                                        <td>{{ detail.current_fonts if 'current_fonts' in detail else detail.current_ratio }}</td>
                                                        <td>{{ detail.recommended_fonts if 'recommended_fonts' in detail else detail.required_ratio }}</td>
                                                    </tr>
                                                {% endfor %}
                                            </table>
                                        {% endif %}
                                    {% endif %}
                                {% endfor %}
                            {% else %}
                                {% if test_data.details %}
                                    <table class="details-table">
                                        <tr>
                                            {% for key in test_data.details[0].keys() %}
                                                <th>{{ key|title }}</th>
                                            {% endfor %}
                                        </tr>
                                        {% for detail in test_data.details %}
                                            <tr>
                                                {% for value in detail.values() %}
                                                    <td>{{ value }}</td>
                                                {% endfor %}
                                            </tr>
                                        {% endfor %}
                                    </table>
                                {% endif %}
                            {% endif %}

                            {% if test_data.recommendations %}
                                <div class="recommendations">
                                    <h3>Recommendations</h3>
                                    {% if test_data.recommendations is mapping %}
                                        <p><strong>Primary:</strong> {{ test_data.recommendations.primary }}</p>
                                        <p><strong>Fallback:</strong> {{ test_data.recommendations.fallback }}</p>
                                    {% else %}
                                        <ul>
                                            {% for rec in test_data.recommendations %}
                                                <li>{{ rec }}</li>
                                            {% endfor %}
                                        </ul>
                                    {% endif %}
                                </div>
                            {% endif %}
                        {% endif %}
                    </div>
                {% endfor %}
            {% endif %}
        </body>
        </html>
        """
        return Template(template).render(results=results)

    def _check_typography(self, driver):
        """Check Japanese typography requirements"""
        return {
            "font_size": self._check_font_sizes(driver),
            "line_height": self._check_line_heights(driver),
            "font_families": self._check_font_families(driver)
        }

    def _check_font_sizes(self, driver):
        """Check font sizes for Japanese text"""
        elements = driver.find_elements(By.CSS_SELECTOR, '*')
        issues = []

        for element in elements:
            try:
                font_size = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).fontSize",
                    element
                )
                size_px = float(font_size.replace('px', ''))
                if size_px < self.config['typography']['min_font_size']:
                    issues.append({
                        'element': element.tag_name,
                        'text': element.text[:50],
                        'current_size': font_size,
                        'minimum_required': f"{self.config['typography']['min_font_size']}px"
                    })
            except Exception:
                continue

        return {
            'issues_found': len(issues),
            'details': issues
        }

    def _check_line_heights(self, driver):
        """Check line heights for Japanese text"""
        issues = []
        min_line_height = self.config['typography']['line_height']

        # Target Japanese text elements
        selectors = [
            'p', 'div:not(:empty)', 'span:not(:empty)',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            '[lang="ja"]', '[lang="ja-JP"]'
        ]

        elements = driver.find_elements(By.CSS_SELECTOR, ', '.join(selectors))

        for element in elements:
            try:
                # Get computed line height
                line_height = driver.execute_script("""
                    var style = window.getComputedStyle(arguments[0]);
                    var lineHeight = style.lineHeight;
                    if (lineHeight === 'normal') {
                        // Approximate 'normal' line height based on font size
                        var fontSize = parseFloat(style.fontSize);
                        return fontSize * 1.2;
                    }
                    return parseFloat(lineHeight);
                """, element)

                # Get font size for comparison
                font_size = driver.execute_script(
                    "return parseFloat(window.getComputedStyle(arguments[0]).fontSize)",
                    element
                )

                # Calculate line height ratio
                line_height_ratio = line_height / font_size

                if line_height_ratio < min_line_height:
                    issues.append({
                        'element': element.tag_name,
                        'text': element.text[:50] + ('...' if len(element.text) > 50 else ''),
                        'current_ratio': round(line_height_ratio, 2),
                        'required_ratio': min_line_height,
                        'font_size': f"{font_size}px",
                        'line_height': f"{line_height}px"
                    })

            except Exception as e:
                self.logger.warning(f"Error checking line height: {str(e)}")
                continue

        return {
            'issues_found': len(issues),
            'min_required_ratio': min_line_height,
            'details': issues
        }

    def _check_font_families(self, driver):
        """Check font families for Japanese text"""
        issues = []
        required_fonts = self.config['typography']['font_families']

        # Target Japanese text elements
        selectors = [
            'p', 'div:not(:empty)', 'span:not(:empty)',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            '[lang="ja"]', '[lang="ja-JP"]'
        ]

        elements = driver.find_elements(By.CSS_SELECTOR, ', '.join(selectors))

        for element in elements:
            try:
                # Get computed font family
                font_family = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).fontFamily",
                    element
                )

                # Check if any required Japanese fonts are included
                has_japanese_font = any(
                    required_font.lower() in font_family.lower()
                    for required_font in required_fonts
                )

                if not has_japanese_font:
                    issues.append({
                        'element': element.tag_name,
                        'text': element.text[:50] + ('...' if len(element.text) > 50 else ''),
                        'current_fonts': font_family,
                        'recommended_fonts': ', '.join(required_fonts),
                        'selector': driver.execute_script("""
                            function getSelector(el) {
                                if (el.id) return '#' + el.id;
                                if (el.className) return '.' + el.className.replace(/\s+/g, '.');
                                return el.tagName.toLowerCase();
                            }
                            return getSelector(arguments[0]);
                        """, element)
                    })

            except Exception as e:
                self.logger.warning(f"Error checking font family: {str(e)}")
                continue

        return {
            'issues_found': len(issues),
            'required_fonts': required_fonts,
            'details': issues,
            'recommendations': {
                'primary': 'Meiryo, "Hiragino Kaku Gothic Pro"',
                'fallback': '"MS PGothic", sans-serif'
            }
        }

    def _check_input_methods(self, driver):
        """Check IME support for input fields"""
        input_elements = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
        issues = []

        for input_element in input_elements:
            ime_mode = driver.execute_script(
                "return window.getComputedStyle(arguments[0]).imeMode",
                input_element
            )
            if ime_mode == 'disabled':
                issues.append({
                    'element': input_element.tag_name,
                    'id': input_element.get_attribute('id'),
                    'name': input_element.get_attribute('name')
                })

        return {
            'total_inputs': len(input_elements),
            'issues_found': len(issues),
            'details': issues
        }

    def _check_encoding(self, url):
        """Check character encoding of the page"""
        try:
            response = requests.get(url)
            detected_encoding = response.encoding

            # Check meta tags for encoding
            soup = BeautifulSoup(response.content, 'html.parser')
            meta_charset = soup.find('meta', charset=True)
            meta_content_type = soup.find('meta', {'http-equiv': 'Content-Type'})

            declared_encoding = None
            if meta_charset:
                declared_encoding = meta_charset['charset']
            elif meta_content_type and 'charset' in meta_content_type.get('content', '').lower():
                content = meta_content_type['content']
                if 'charset=' in content.lower():
                    declared_encoding = content.split('charset=')[-1].strip()

            valid_encodings = ['utf-8', 'shift_jis', 'euc-jp']
            is_valid = detected_encoding.lower() in [enc.lower() for enc in valid_encodings]

            return {
                "detected": detected_encoding,
                "declared": declared_encoding,
                "valid": is_valid,
                "recommended": "UTF-8",
                "details": {
                    "meta_charset_present": bool(meta_charset),
                    "content_type_present": bool(meta_content_type),
                    "supported_encodings": valid_encodings
                }
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_screen_reader_compatibility(self, driver):
        """Check screen reader compatibility for Japanese content"""
        issues = []

        # Check lang attribute
        html_element = driver.find_element(By.TAG_NAME, 'html')
        lang = html_element.get_attribute('lang')
        if not lang or not lang.startswith('ja'):
            issues.append({
                'type': 'language',
                'message': 'HTML lang attribute should be set to "ja" or "ja-JP"'
            })

        # Check for proper heading structure
        headings = driver.find_elements(By.CSS_SELECTOR, 'h1, h2, h3, h4, h5, h6')
        current_level = 0
        for heading in headings:
            level = int(heading.tag_name[1])
            if level - current_level > 1:
                issues.append({
                    'type': 'heading_structure',
                    'message': f'Heading level skipped from h{current_level} to h{level}',
                    'element': heading.text[:50]
                })
            current_level = level

        return {
            'issues_found': len(issues),
            'details': issues
        }

    def _check_ruby_text(self, url):
        """Check ruby text (furigana) implementation"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            ruby_elements = soup.find_all('ruby')

            issues = []
            issues_count = 0

            for ruby in ruby_elements:
                rt = ruby.find('rt')
                rp = ruby.find_all('rp')

                # Check if ruby elements are properly formed
                if not rt or len(rp) != 2:
                    issues_count += 1
                    issues.append({
                        'element': str(ruby)[:100],
                        'has_rt': bool(rt),
                        'has_rp': len(rp) == 2,
                        'issue': 'Improper ruby text implementation'
                    })

            return {
                'total': len(ruby_elements),
                'issues_found': issues_count,
                'with_rt': sum(1 for r in ruby_elements if r.find('rt')),
                'with_rp': sum(1 for r in ruby_elements if len(r.find_all('rp')) == 2),
                'properly_formed': len(ruby_elements) - issues_count,
                'details': issues,
                'recommendations': [
                    'Use proper <ruby> markup for all kanji',
                    'Include both <rt> and <rp> elements',
                    'Ensure ruby text is readable and properly sized',
                    'Consider automatic ruby text generation for complex kanji'
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_text_resize(self, driver):
        """Check text resize compatibility"""
        original_sizes = {}
        issues = []
        total_tested = 0

        # Get original text sizes
        text_elements = driver.find_elements(By.CSS_SELECTOR, 'p, span, div:not(:empty), h1, h2, h3, h4, h5, h6')
        for element in text_elements:
            try:
                original_sizes[element] = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).fontSize",
                    element
                )
                total_tested += 1
            except Exception:
                continue

        # Resize text to 200%
        driver.execute_script("document.body.style.zoom = '200%'")

        # Check for text overlap or clipping
        for element in original_sizes.keys():
            try:
                new_size = driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).fontSize",
                    element
                )
                is_visible = driver.execute_script(
                    """
                    var elem = arguments[0];
                    var style = window.getComputedStyle(elem);
                    return style.display !== 'none' && 
                           style.visibility !== 'hidden' && 
                           style.opacity !== '0';
                    """,
                    element
                )

                if not is_visible:
                    issues.append({
                        'element': element.tag_name,
                        'text': element.text[:50],
                        'issue': 'Text hidden after resize'
                    })
            except Exception:
                continue

        # Reset zoom
        driver.execute_script("document.body.style.zoom = '100%'")

        return {
            'total_tested': total_tested,
            'issues_found': len(issues),
            'details': issues
        }

    def _check_color_contrast(self, driver):
        """Check color contrast ratios"""
        issues = []

        text_elements = driver.find_elements(By.CSS_SELECTOR, 'p, span, div:not(:empty), h1, h2, h3, h4, h5, h6, a')
        for element in text_elements:
            try:
                # Get text and background colors
                style = driver.execute_script(
                    """
                    var style = window.getComputedStyle(arguments[0]);
                    return {
                        color: style.color,
                        backgroundColor: style.backgroundColor
                    };
                    """,
                    element
                )

                # Calculate contrast ratio
                contrast_ratio = self._calculate_contrast_ratio(
                    self._parse_color(style['color']),
                    self._parse_color(style['backgroundColor'])
                )

                if contrast_ratio < 4.5:  # WCAG AA standard
                    issues.append({
                        'element': element.tag_name,
                        'text': element.text[:50],
                        'contrast_ratio': round(contrast_ratio, 2),
                        'required_ratio': 4.5
                    })
            except Exception:
                continue

        return {
            'issues_found': len(issues),
            'details': issues
        }

    def _parse_color(self, color_str):
        """Parse color string to RGB values"""
        import re
        rgb = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', color_str)
        if rgb:
            return tuple(map(int, rgb.groups()))
        return (0, 0, 0)  # Default to black if parsing fails

    def _calculate_contrast_ratio(self, color1, color2):
        """Calculate contrast ratio between two colors"""
        l1 = self._calculate_luminance(color1)
        l2 = self._calculate_luminance(color2)

        if l1 > l2:
            return (l1 + 0.05) / (l2 + 0.05)
        return (l2 + 0.05) / (l1 + 0.05)

    def _calculate_luminance(self, rgb):
        """Calculate relative luminance"""
        r, g, b = [x / 255 for x in rgb]
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    def _check_form_zero(self, url):
        """Implement Form Zero accessibility checks"""
        try:
            if not self.driver:
                self.driver = self._setup_driver()

            self.driver.get(url)
            results = {
                "keyboard_navigation": self._check_keyboard_navigation(self.driver),
                "focus_visibility": self._check_focus_visibility(self.driver),
                "input_methods": self._check_input_methods(self.driver),
                "error_identification": self._check_error_identification(self.driver),
                "timeout_handling": self._check_timeout_handling(self.driver)
            }

            # Add overall assessment
            total_issues = sum(check.get('issues_found', 0) for check in results.values())
            results["summary"] = {
                "total_issues": total_issues,
                "status": "Pass" if total_issues == 0 else "Fail",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return results
        except Exception as e:
            return {"error": str(e)}

    def _check_focus_visibility(self, driver):
        """Check if focus is visible on all interactive elements"""
        try:
            focusable_elements = driver.find_elements(By.CSS_SELECTOR,
                                                      'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])')

            issues = []
            for element in focusable_elements:
                try:
                    # Focus the element
                    driver.execute_script("arguments[0].focus();", element)

                    # Get computed style after focus
                    style = driver.execute_script("""
                        const style = window.getComputedStyle(arguments[0]);
                        return {
                            outlineStyle: style.outlineStyle,
                            outlineWidth: style.outlineWidth,
                            outlineColor: style.outlineColor,
                            boxShadow: style.boxShadow
                        }
                    """, element)

                    # Check if focus is visible
                    has_visible_focus = (
                            style['outlineStyle'] != 'none' or
                            style['boxShadow'] != 'none'
                    )

                    if not has_visible_focus:
                        issues.append({
                            'element': element.tag_name,
                            'id': element.get_attribute('id'),
                            'class': element.get_attribute('class'),
                            'styles': style
                        })
                except Exception as e:
                    print(f"Error checking focus for element: {str(e)}")

            return {
                "issues_found": len(issues),
                "issues": issues,
                "recommendations": [
                    "Ensure all interactive elements have visible focus indicators",
                    "Use outline or box-shadow for focus visibility",
                    "Consider high contrast focus indicators"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_timeout_handling(self, driver):
        """Check timeout handling for forms and sessions"""
        try:
            forms = driver.find_elements(By.TAG_NAME, 'form')
            issues = []

            for form in forms:
                # Check for auto-save functionality
                auto_save = driver.execute_script("""
                    return arguments[0].hasAttribute('data-autosave') || 
                           Array.from(arguments[0].elements).some(e => e.hasAttribute('data-autosave'));
                """, form)

                # Check for session timeout warnings
                timeout_warning = driver.execute_script("""
                    return arguments[0].hasAttribute('data-timeout-warning') ||
                           document.querySelector('[data-timeout-warning]') !== null;
                """, form)

                if not (auto_save or timeout_warning):
                    issues.append({
                        'form_id': form.get_attribute('id'),
                        'form_action': form.get_attribute('action'),
                        'missing_features': {
                            'auto_save': not auto_save,
                            'timeout_warning': not timeout_warning
                        }
                    })

            return {
                "issues_found": len(issues),
                "issues": issues,
                "recommendations": [
                    "Implement auto-save functionality for long forms",
                    "Add session timeout warnings",
                    "Provide option to extend session",
                    "Ensure form data is not lost on timeout"
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    def _check_keyboard_navigation(self, driver):
        """Check keyboard navigation for Japanese forms and elements"""
        try:
            focusable_elements = driver.find_elements(By.CSS_SELECTOR,
                                                      'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])')

            issues = []
            current_element = None
            tab_order = []

            for element in focusable_elements:
                try:
                    # Try to focus the element
                    driver.execute_script("arguments[0].focus();", element)

                    # Get the currently focused element
                    active_element = driver.switch_to.active_element

                    # Check if focus was successful
                    if active_element != element:
                        issues.append({
                            'element': element.tag_name,
                            'id': element.get_attribute('id'),
                            'issue': 'Element cannot receive keyboard focus'
                        })
                        continue

                    # Check for visible focus indicator
                    focus_visible = self._check_focus_indicator(element)
                    if not focus_visible:
                        issues.append({
                            'element': element.tag_name,
                            'id': element.get_attribute('id'),
                            'issue': 'No visible focus indicator'
                        })

                    # Check for proper tab order
                    tab_index = element.get_attribute('tabindex')
                    if tab_index and int(tab_index) > 0:
                        tab_order.append({
                            'element': element,
                            'tabindex': int(tab_index)
                        })

                    # For Japanese input fields, check IME activation
                    if element.tag_name.lower() in ['input', 'textarea']:
                        ime_mode = driver.execute_script(
                            "return window.getComputedStyle(arguments[0]).imeMode",
                            element
                        )
                        if ime_mode == 'disabled':
                            issues.append({
                                'element': element.tag_name,
                                'id': element.get_attribute('id'),
                                'issue': 'IME disabled for Japanese input'
                            })

                except Exception as e:
                    print(f"Error checking element: {str(e)}")
                    continue

            # Check tab order sequence
            if tab_order:
                tab_order.sort(key=lambda x: x['tabindex'])
                for i in range(len(tab_order) - 1):
                    if tab_order[i + 1]['tabindex'] - tab_order[i]['tabindex'] > 1:
                        issues.append({
                            'element': tab_order[i]['element'].tag_name,
                            'id': tab_order[i]['element'].get_attribute('id'),
                            'issue': 'Non-sequential tab order'
                        })

            return {
                'issues_found': len(issues),
                'issues': issues,
                'recommendations': [
                    'Ensure all interactive elements are keyboard accessible',
                    'Maintain logical tab order',
                    'Provide visible focus indicators',
                    'Enable IME for Japanese text input fields'
                ]
            }

        except Exception as e:
            return {'error': str(e)}

    def _check_focus_indicator(self, element):
        """Check if element has visible focus indicator"""
        try:
            # Get computed styles
            styles = self.driver.execute_script("""
                const style = window.getComputedStyle(arguments[0]);
                return {
                    outlineStyle: style.outlineStyle,
                    outlineWidth: style.outlineWidth,
                    outlineColor: style.outlineColor,
                    boxShadow: style.boxShadow,
                    borderStyle: style.borderStyle,
                    backgroundColor: style.backgroundColor
                };
            """, element)

            # Check for visible focus indicators
            has_outline = (
                    styles['outlineStyle'] != 'none' and
                    styles['outlineWidth'] != '0px'
            )
            has_shadow = styles['boxShadow'] != 'none'
            has_border = styles['borderStyle'] != 'none'
            has_bg = styles['backgroundColor'] != 'transparent'

            return has_outline or has_shadow or has_border or has_bg

        except Exception as e:
            print(f"Error checking focus indicator: {str(e)}")
            return False

    def _check_error_identification(self, driver):
        """Check error identification in Japanese forms"""
        try:
            forms = driver.find_elements(By.TAG_NAME, 'form')
            issues = []

            for form in forms:
                # Check for error message containers
                error_containers = form.find_elements(By.CSS_SELECTOR,
                                                      '[role="alert"], .error, .invalid-feedback')

                # Check input fields
                inputs = form.find_elements(By.CSS_SELECTOR,
                                            'input, select, textarea')

                for input_field in inputs:
                    # Check for aria-invalid
                    aria_invalid = input_field.get_attribute('aria-invalid')

                    # Check for error message association
                    error_id = input_field.get_attribute('aria-errormessage')
                    if error_id:
                        try:
                            error_message = driver.find_element(By.ID, error_id)
                            if not error_message:
                                issues.append({
                                    'element': input_field.tag_name,
                                    'id': input_field.get_attribute('id'),
                                    'issue': 'Missing referenced error message'
                                })
                        except:
                            issues.append({
                                'element': input_field.tag_name,
                                'id': input_field.get_attribute('id'),
                                'issue': 'Invalid error message reference'
                            })

                    # Check for Japanese error message clarity
                    for container in error_containers:
                        if container.text:
                            if not self._is_clear_japanese_error(container.text):
                                issues.append({
                                    'element': container.tag_name,
                                    'text': container.text,
                                    'issue': 'Unclear Japanese error message'
                                })

            return {
                'issues_found': len(issues),
                'issues': issues,
                'recommendations': [
                    'Use clear and polite Japanese error messages',
                    'Ensure error messages are properly associated with inputs',
                    'Provide both visual and programmatic error indicators',
                    'Consider cultural context in error presentation'
                ]
            }

        except Exception as e:
            return {'error': str(e)}

    def _is_clear_japanese_error(self, text):
        """Check if Japanese error message is clear and polite"""
        # Common polite Japanese error patterns
        polite_patterns = [
            'ください',  # Please
            'お願いします',  # Please
            'してください',  # Please do
            'です',  # Polite copula
            'ます',  # Polite verb ending
        ]

        # Check if message uses polite language
        is_polite = any(pattern in text for pattern in polite_patterns)

        # Check if message length is appropriate
        is_appropriate_length = 10 <= len(text) <= 100

        # Check if message contains explanation
        has_explanation = ('が' in text or 'を' in text or 'は' in text)

        return is_polite and is_appropriate_length and has_explanation

    def _get_element_path(self, element):
        """Get unique CSS selector path for an element"""
        try:
            return self.driver.execute_script("""
                function getElementPath(element) {
                    const path = [];
                    while (element && element.nodeType === Node.ELEMENT_NODE) {
                        let selector = element.nodeName.toLowerCase();

                        if (element.id) {
                            selector += '#' + element.id;
                            path.unshift(selector);
                            break;
                        } else {
                            let sibling = element;
                            let nth = 1;

                            while (sibling.previousElementSibling) {
                                sibling = sibling.previousElementSibling;
                                if (sibling.nodeName.toLowerCase() === selector) nth++;
                            }

                            if (nth !== 1) selector += ":nth-of-type("+nth+")";
                        }

                        path.unshift(selector);
                        element = element.parentNode;
                    }

                    return path.join(' > ');
                }
                return getElementPath(arguments[0]);
            """, element)
        except Exception as e:
            return f"Path extraction failed: {str(e)}"

    def _get_wcag_level(self, check_type):
        """Get WCAG and JIS compliance levels for a check"""
        return JAPANESE_WCAG_MAPPING.get(check_type, {
            'wcag': 'Custom',
            'level': 'Custom',
            'jis': 'Custom',
            'category': 'Custom'
        })

    def _create_issue(self, check_type, element, issue_type, description, **kwargs):
        """Create a standardized issue with path and compliance information"""
        issue = JapaneseAccessibilityIssue(check_type, element, issue_type, description)

        if element:
            issue.set_path(self._get_element_path(element))

        issue.set_compliance_info(self._get_wcag_level(check_type))

        for key, value in kwargs.items():
            issue.add_info(key, value)

        return issue.to_dict()