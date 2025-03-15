"""
WCAG 2.2 custom tests module
Provides specialized tests for WCAG 2.2 success criteria that are not fully covered by existing tools.
"""

import os
import json
import logging
import time
import tempfile
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from jinja2 import Template

from utils.report_generators import generate_html_report
from ..core.base_tester import BaseAccessibilityTester


class WCAG22Tester(BaseAccessibilityTester):
    """Custom tester for WCAG 2.2 success criteria."""

    def __init__(self):
        super().__init__("wcag22")
        self.logger = logging.getLogger(self.__class__.__name__)
        self.driver = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # WCAG 2.2 success criteria information
        self.wcag22_criteria = {
            "2.4.11": {
                "name": "Focus Not Obscured (Minimum)",
                "level": "AA",
                "description": "When a user interface component receives keyboard focus, the component is not entirely hidden due to author-created content."
            },
            "2.4.12": {
                "name": "Focus Not Obscured (Enhanced)",
                "level": "AAA",
                "description": "When a user interface component receives keyboard focus, no part of the component is hidden by author-created content."
            },
            "2.4.13": {
                "name": "Focus Appearance",
                "level": "AAA",
                "description": "When a user interface component receives keyboard focus, the focus indicator is clearly visible and sufficient."
            },
            "2.5.7": {
                "name": "Dragging Movements",
                "level": "AA",
                "description": "All functionality that uses a dragging movement can be operated by a single pointer without dragging, unless dragging is essential."
            },
            "2.5.8": {
                "name": "Target Size (Minimum)",
                "level": "AA",
                "description": "The size of the target for pointer inputs is at least 24 by 24 CSS pixels, except where alternatives, the target is inline, the size is determined by user agent and not modified by the author, or the presentation is essential."
            },
            "3.2.6": {
                "name": "Consistent Help",
                "level": "A",
                "description": "If a web page contains any of these help mechanisms: human contact details, human contact mechanism, self-help option, or a fully automated contact mechanism, then they occur in the same relative order on each web page where they appear."
            },
            "3.3.7": {
                "name": "Accessible Authentication",
                "level": "A",
                "description": "For each step in an authentication process that relies on a cognitive function test, at least one other authentication method that does not rely on a cognitive function test, or a mechanism is available to assist the user in completing the cognitive function test."
            },
            "3.3.8": {
                "name": "Accessible Authentication (No Exception)",
                "level": "AAA",
                "description": "For each step in an authentication process, an authentication method is available that does not rely on a cognitive function test."
            },
            "3.3.9": {
                "name": "Redundant Entry",
                "level": "A",
                "description": "Information previously entered by or provided to the user that is required to be entered again is auto-populated, or available for the user to select."
            }
        }

    def _setup_driver(self):
        """Setup webdriver for browser-based tests."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1366,768')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def test_accessibility(self, url, test_dir=None):
        """Run WCAG 2.2 specific accessibility tests on the given URL."""
        try:
            if test_dir:
                self.output_dir = test_dir
            else:
                self.output_dir = os.path.join(os.getcwd(), "Reports", f"wcag22_test_{self.timestamp}")
                os.makedirs(self.output_dir, exist_ok=True)

            self.driver = self._setup_driver()

            # Initialize results dictionary
            results = {
                "tool": "wcag22",
                "url": url,
                "timestamp": self.timestamp,
                "test_dir": self.output_dir,
                "results": {}
            }

            # Load the URL
            self.driver.get(url)
            time.sleep(3)  # Allow page to load completely

            # Run tests for each WCAG 2.2 criterion
            # results["results"]["2.4.11"] = self._test_2_4_11_focus_not_obscured()
            # results["results"]["2.4.13"] = self._test_2_4_13_focus_appearance()
            # results["results"]["2.5.7"] = self._test_2_5_7_dragging_movements()
            # results["results"]["2.5.8"] = self._test_2_5_8_target_size()
            # results["results"]["3.2.6"] = self._test_3_2_6_consistent_help()
            # results["results"]["3.3.7"] = self._test_3_3_7_accessible_authentication()
            # results["results"]["3.3.9"] = self._test_3_3_9_redundant_entry()
            results["results"]["2.4.7"] = self._test_2_4_7_focus_visible()  # New test
            results["results"]["2.4.11"] = self._test_2_4_11_focus_not_obscured()  # Existing
            results["results"]["1.4.11"] = self._test_1_4_11_non_text_contrast()  # New test
            results["results"]["1.4.12"] = self._test_1_4_12_text_spacing()  # New test
            results["results"]["2.5.7"] = self._test_2_5_7_dragging_movements_enhanced()  # Enhanced
            results["results"]["2.5.8"] = self._test_2_5_8_target_size()  # Existing
            results["results"]["3.2.6"] = self._test_3_2_6_consistent_help()  # Existing
            results["results"]["3.3.7"] = self._test_3_3_7_accessible_authentication()  # Existing
            results["results"]["3.3.9"] = self._test_3_3_9_redundant_entry_enhanced()  # Enhanced

            # Add metadata
            results["summary"] = self._create_summary(results["results"])
            results["total_issues"] = results["summary"]["total_issues"]

            return results

        except Exception as e:
            error_message = f"Error running WCAG 2.2 tests: {str(e)}"
            self.logger.error(error_message)
            return {
                "tool": "wcag22",
                "url": url,
                "timestamp": self.timestamp,
                "error": error_message,
                "test_dir": self.output_dir if hasattr(self, 'output_dir') else test_dir
            }
        finally:
            if self.driver:
                self.driver.quit()

    def _test_2_4_11_focus_not_obscured(self):
        """
        Test for WCAG 2.2 Success Criterion 2.4.11: Focus Not Obscured (Minimum).

        When a user interface component receives keyboard focus,
        the component is not entirely hidden due to author-created content.
        """
        self.logger.info("Testing 2.4.11: Focus Not Obscured (Minimum)")

        # Initialize results
        criterion_results = {
            "criterion": "2.4.11",
            "name": self.wcag22_criteria["2.4.11"]["name"],
            "level": self.wcag22_criteria["2.4.11"]["level"],
            "description": self.wcag22_criteria["2.4.11"]["description"],
            "issues": [],
            "passed": True
        }

        try:
            # Instead of collecting all elements first and then testing,
            # test one element at a time to avoid stale references
            selectors = [
                "a", "button", "input:not([type='hidden'])", "select", "textarea",
                "[tabindex]:not([tabindex='-1'])"
            ]

            # Create a safer version of the obscured check script
            obscured_check_script = """
                    function checkIfObscured(element) {
                        if (!element || !document.body.contains(element)) {
                            return { error: "Element not in DOM" };
                        }

                        try {
                            var rect = element.getBoundingClientRect();

                            // Skip elements not in viewport
                            if (rect.top > window.innerHeight || rect.bottom < 0 ||
                                rect.left > window.innerWidth || rect.right < 0) {
                                return { error: "Element not in viewport" };
                            }

                            // Get element information
                            var elementInfo = {
                                tagName: element.tagName.toLowerCase(),
                                id: element.id || "",
                                className: element.className || "",
                                text: element.textContent ? element.textContent.trim().substring(0, 50) : "[No text]"
                            };

                            // Focus the element
                            element.focus();

                            // Check center point for obscured status
                            var centerX = rect.left + rect.width / 2;
                            var centerY = rect.top + rect.height / 2;

                            var elementAtPoint = document.elementFromPoint(centerX, centerY);

                            // Element is obscured if what's at that point isn't the element or child
                            var isObscured = false;
                            if (elementAtPoint) {
                                isObscured = (elementAtPoint !== element) && 
                                            !element.contains(elementAtPoint) && 
                                            !elementAtPoint.contains(element);
                            }

                            return {
                                isObscured: isObscured,
                                elementInfo: elementInfo
                            };
                        } catch (e) {
                            return { error: e.message };
                        }
                    }

                    return checkIfObscured(arguments[0]);
                """

            # Test elements for each selector one by one
            for selector in selectors:
                # Get elements matching this selector
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                self.logger.info(f"Found {len(elements)} {selector} elements")

                # Test a maximum of 50 elements per selector to avoid timeouts
                for element in elements[:50]:
                    try:
                        # Scroll element into view (important for focus!)
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        time.sleep(0.2)  # Brief pause after scrolling

                        # Check if element is obscured when focused
                        result = self.driver.execute_script(obscured_check_script, element)

                        # Handle error in result
                        if "error" in result:
                            self.logger.debug(f"Skipping element: {result['error']}")
                            continue

                        # If element is obscured, add to issues
                        if result["isObscured"]:
                            criterion_results["issues"].append({
                                "element": result["elementInfo"]["tagName"],
                                "element_info": {
                                    "id": result["elementInfo"]["id"],
                                    "class": result["elementInfo"]["className"],
                                    "text": result["elementInfo"]["text"]
                                },
                                "message": "Element is obscured when it receives focus"
                            })
                            criterion_results["passed"] = False

                    except Exception as e:
                        # Log error but continue with next element
                        self.logger.debug(f"Error testing individual element: {str(e)}")
                        continue

        except Exception as e:
            self.logger.error(f"Error in focus not obscured test: {str(e)}")
            criterion_results["error"] = str(e)

        # Finalize results
        if criterion_results["passed"]:
            criterion_results["summary"] = "All focusable elements remain visible when focused"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} elements that are obscured when they receive focus"

        return criterion_results

    def _test_2_4_13_focus_appearance(self):
        """
        Test for WCAG 2.2 Success Criterion 2.4.13: Focus Appearance (Enhanced).

        When a component receives keyboard focus, the focus indicator:
        - Has a contrast ratio of at least 3:1 between focused and unfocused states
        - Has a contrast ratio of at least 3:1 against adjacent colors
        - Is at least 2 CSS pixels thick
        - Is not entirely hidden by author-created content
        """
        self.logger.info("Testing 2.4.13: Focus Appearance")

        criterion_results = {
            "criterion": "2.4.13",
            "name": self.wcag22_criteria["2.4.13"]["name"],
            "level": self.wcag22_criteria["2.4.13"]["level"],
            "description": self.wcag22_criteria["2.4.13"]["description"],
            "issues": [],
            "passed": True
        }

        # Get all focusable elements
        focusable_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                       "a, button, input, select, textarea, [tabindex]:not([tabindex='-1'])")

        # Test each element
        for element in focusable_elements:
            try:
                # Get unfocused styles
                unfocused_styles = self.driver.execute_script("""
                    var el = arguments[0];
                    var style = window.getComputedStyle(el);
                    return {
                        outlineWidth: style.outlineWidth,
                        outlineStyle: style.outlineStyle,
                        outlineColor: style.outlineColor,
                        borderWidth: style.borderWidth,
                        borderStyle: style.borderStyle,
                        borderColor: style.borderColor,
                        boxShadow: style.boxShadow,
                        backgroundColor: style.backgroundColor
                    };
                """, element)

                # Focus the element
                self.driver.execute_script("arguments[0].focus();", element)
                time.sleep(0.2)  # Wait for focus styles to apply

                # Get focused styles
                focused_styles = self.driver.execute_script("""
                    var el = arguments[0];
                    var style = window.getComputedStyle(el);
                    return {
                        outlineWidth: style.outlineWidth,
                        outlineStyle: style.outlineStyle,
                        outlineColor: style.outlineColor,
                        borderWidth: style.borderWidth,
                        borderStyle: style.borderStyle,
                        borderColor: style.borderColor,
                        boxShadow: style.boxShadow,
                        backgroundColor: style.backgroundColor
                    };
                """, element)

                # Check focus indicator thickness (outline or border)
                outline_width = self._parse_pixel_value(focused_styles.get("outlineWidth", "0px"))
                border_width = self._parse_pixel_value(focused_styles.get("borderWidth", "0px"))

                # Check if visible focus indicator exists
                has_visible_focus = (
                        (outline_width > 0 and focused_styles.get("outlineStyle") != "none") or
                        (border_width > 0 and focused_styles.get("borderStyle") != "none") or
                        (focused_styles.get("boxShadow", "none") != "none") or
                        (unfocused_styles.get("backgroundColor") != focused_styles.get("backgroundColor"))
                )

                if not has_visible_focus:
                    criterion_results["issues"].append({
                        "element": element.tag_name,
                        "element_info": {
                            "id": element.get_attribute("id"),
                            "class": element.get_attribute("class"),
                            "text": element.text if element.text else "[No text]"
                        },
                        "message": "Element has no visible focus indicator",
                        "focused_styles": focused_styles,
                        "unfocused_styles": unfocused_styles
                    })
                    criterion_results["passed"] = False
                    continue

                # Check if focus indicator is thick enough (≥ 2px)
                indicator_thick_enough = outline_width >= 2 or border_width >= 2

                if not indicator_thick_enough and focused_styles.get("boxShadow", "none") == "none":
                    criterion_results["issues"].append({
                        "element": element.tag_name,
                        "element_info": {
                            "id": element.get_attribute("id"),
                            "class": element.get_attribute("class"),
                            "text": element.text if element.text else "[No text]"
                        },
                        "message": "Focus indicator is less than 2px thick",
                        "outline_width": f"{outline_width}px",
                        "border_width": f"{border_width}px"
                    })
                    criterion_results["passed"] = False

            except Exception as e:
                self.logger.error(f"Error testing focus appearance for {element.tag_name}: {str(e)}")

        if criterion_results["passed"]:
            criterion_results["summary"] = "All focusable elements have adequate focus indicators"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} elements with inadequate focus indicators"

        return criterion_results

    def _test_2_5_7_dragging_movements(self):
        """
        Test for WCAG 2.2 Success Criterion 2.5.7: Dragging Movements.

        All functionality that uses a dragging movement can be operated by a single pointer
        without dragging, unless dragging is essential.
        """
        self.logger.info("Testing 2.5.7: Dragging Movements")

        criterion_results = {
            "criterion": "2.5.7",
            "name": self.wcag22_criteria["2.5.7"]["name"],
            "level": self.wcag22_criteria["2.5.7"]["level"],
            "description": self.wcag22_criteria["2.5.7"]["description"],
            "issues": [],
            "passed": True  # Assume passing until issues are found
        }

        # Look for common draggable elements
        draggable_selectors = [
            "[draggable='true']",
            ".draggable",
            ".slider",
            ".sortable",
            ".ui-draggable",
            ".ui-slider",
            ".ui-sortable",
            "[role='slider']",
            "input[type='range']"
        ]

        draggable_elements = self.driver.find_elements(By.CSS_SELECTOR, ", ".join(draggable_selectors))

        if not draggable_elements:
            criterion_results["summary"] = "No draggable elements found on the page"
            return criterion_results

        # Check each draggable element
        for element in draggable_elements:
            try:
                element_tag = element.tag_name
                element_type = element.get_attribute("type")
                element_role = element.get_attribute("role")
                element_id = element.get_attribute("id")
                element_class = element.get_attribute("class")

                # Special case for range inputs (sliders)
                if element_tag == "input" and element_type == "range":
                    # Check if there are arrow key controls or precise input option
                    has_alternative = False

                    # Check if there's a linked input field with the same name or id
                    input_name = element.get_attribute("name")
                    if input_name:
                        linked_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                                                                  f"input[type='number'][name='{input_name}']")
                        has_alternative = len(linked_inputs) > 0

                    if not has_alternative:
                        criterion_results["issues"].append({
                            "element": element_tag,
                            "element_info": {
                                "id": element_id,
                                "class": element_class,
                                "type": element_type
                            },
                            "message": "Range input (slider) without alternative non-dragging mechanism"
                        })
                        criterion_results["passed"] = False

                # Check other draggable elements
                elif element.get_attribute("draggable") == "true" or "draggable" in element_class.lower():
                    # Look for alternative controls, buttons, or options for the same functionality
                    # Example: Check for buttons nearby with move or sort text
                    element_location = element.location
                    alt_controls = self.driver.find_elements(By.CSS_SELECTOR,
                                                             "button, a.button, [role='button'], input[type='button']")

                    has_alternative = False
                    for control in alt_controls:
                        control_text = control.text.lower()
                        if any(keyword in control_text for keyword in
                               ["move", "sort", "order", "position", "up", "down"]):
                            has_alternative = True
                            break

                    if not has_alternative:
                        criterion_results["issues"].append({
                            "element": element_tag,
                            "element_info": {
                                "id": element_id,
                                "class": element_class,
                                "draggable": "true"
                            },
                            "message": "Draggable element without detected alternative non-dragging mechanism"
                        })
                        criterion_results["passed"] = False

                # Check for sliders
                elif "slider" in element_class.lower() or element_role == "slider":
                    # Similar checks for sliders
                    has_alternative = False

                    # Look for related inputs or arrow controls
                    parent_element = element.find_element(By.XPATH, "./..")
                    input_fields = parent_element.find_elements(By.CSS_SELECTOR,
                                                                "input[type='number'], input[type='text']")
                    arrow_buttons = parent_element.find_elements(By.CSS_SELECTOR,
                                                                 "button.increment, button.decrement, button.up, button.down, [aria-label*='increase'], [aria-label*='decrease']")

                    has_alternative = len(input_fields) > 0 or len(arrow_buttons) > 0

                    if not has_alternative:
                        criterion_results["issues"].append({
                            "element": element_tag,
                            "element_info": {
                                "id": element_id,
                                "class": element_class,
                                "role": element_role
                            },
                            "message": "Slider element without detected alternative non-dragging mechanism"
                        })
                        criterion_results["passed"] = False

            except Exception as e:
                self.logger.error(f"Error testing dragging movements for {element.tag_name}: {str(e)}")

        if criterion_results["passed"]:
            criterion_results["summary"] = "All draggable elements have alternative non-dragging mechanisms"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} elements with dragging functionality without alternatives"

        return criterion_results

    def _test_2_5_8_target_size(self):
        """
        Test for WCAG 2.2 Success Criterion 2.5.8: Target Size (Minimum).

        The size of the target for pointer inputs is at least 24 by 24 CSS pixels.
        """
        self.logger.info("Testing 2.5.8: Target Size (Minimum)")

        criterion_results = {
            "criterion": "2.5.8",
            "name": self.wcag22_criteria["2.5.8"]["name"],
            "level": self.wcag22_criteria["2.5.8"]["level"],
            "description": self.wcag22_criteria["2.5.8"]["description"],
            "issues": [],
            "passed": True
        }

        # Get all interactive/clickable elements
        target_selectors = [
            "a", "button", "input[type='button']", "input[type='submit']",
            "input[type='reset']", "input[type='checkbox']", "input[type='radio']",
            "select", "[role='button']", "[role='link']", "[role='checkbox']",
            "[role='radio']", "[role='tab']", "[role='menuitem']", "[tabindex]:not([tabindex='-1'])"
        ]

        target_elements = self.driver.find_elements(By.CSS_SELECTOR, ", ".join(target_selectors))

        # Add potential click handlers
        js_clickable_elements = self.driver.execute_script("""
            const potentialClickables = [];
            const allElements = document.querySelectorAll('*');

            for (const el of allElements) {
                // Check for click event handlers or onclick attribute
                if (el.onclick || el.getAttribute('onclick') || 
                    el.addEventListener && el._listeners && el._listeners.click) {
                    potentialClickables.push(el);
                }
            }

            return potentialClickables;
        """)

        # Combine the lists, ensuring no duplicates
        all_targets = list(set(target_elements + js_clickable_elements))

        # Test each target element
        for element in all_targets:
            try:
                # Get element size
                size_info = self.driver.execute_script("""
                    var el = arguments[0];
                    var rect = el.getBoundingClientRect();
                    var computedStyle = window.getComputedStyle(el);

                    return {
                        width: rect.width,
                        height: rect.height,
                        displayType: computedStyle.display,
                        tagName: el.tagName.toLowerCase(),
                        isInlineText: (
                            computedStyle.display === 'inline' && 
                            el.textContent.trim() !== ''
                        )
                    };
                """, element)

                # Skip exceptions noted in the success criterion
                is_exception = (
                    # Inline text links exception
                        size_info["isInlineText"] or
                        # User agent controlled size exception
                        size_info["tagName"] in ["input", "select", "textarea"] or
                        # Small display area adjustment
                        (self.driver.execute_script("return window.innerWidth < 640;"))
                )

                if not is_exception:
                    # Check if either dimension is under 24px
                    if size_info["width"] < 24 or size_info["height"] < 24:
                        criterion_results["issues"].append({
                            "element": element.tag_name,
                            "element_info": {
                                "id": element.get_attribute("id"),
                                "class": element.get_attribute("class"),
                                "text": element.text if element.text else "[No text]"
                            },
                            "size": {
                                "width": f"{size_info['width']}px",
                                "height": f"{size_info['height']}px"
                            },
                            "message": f"Target size ({size_info['width']}x{size_info['height']}px) is smaller than minimum 24x24px"
                        })
                        criterion_results["passed"] = False

            except Exception as e:
                self.logger.error(f"Error testing target size for {element.tag_name}: {str(e)}")

        if criterion_results["passed"]:
            criterion_results["summary"] = "All applicable targets meet the minimum size requirement of 24x24px"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} targets smaller than the required minimum size"

        return criterion_results

    def _test_3_2_6_consistent_help(self):
        """
        Test for WCAG 2.2 Success Criterion 3.2.6: Consistent Help.

        If a web page contains help mechanisms, they occur in the same relative order
        on each page where they appear.
        """
        self.logger.info("Testing 3.2.6: Consistent Help")

        criterion_results = {
            "criterion": "3.2.6",
            "name": self.wcag22_criteria["3.2.6"]["name"],
            "level": self.wcag22_criteria["3.2.6"]["level"],
            "description": self.wcag22_criteria["3.2.6"]["description"],
            "issues": [],
            "passed": True
        }

        # Find help mechanisms on the current page
        help_mechanisms = self._find_help_mechanisms()

        if not help_mechanisms:
            criterion_results["summary"] = "No help mechanisms detected on the page"
            return criterion_results

        # Store help mechanisms for comparison
        criterion_results["help_mechanisms"] = help_mechanisms
        criterion_results["summary"] = f"Found {len(help_mechanisms)} help mechanisms on the page"

        # For this test to be comprehensive, we'd need to compare across multiple pages
        # Since we're only testing one page at a time, we'll just record what was found
        criterion_results["manual_check_required"] = True
        criterion_results["manual_check_instructions"] = (
            "This test requires checking multiple pages to verify consistent placement of help mechanisms. "
            "The detected help mechanisms on this page are listed for manual comparison."
        )

        return criterion_results

    def _find_help_mechanisms(self):
        """Find help mechanisms on the current page."""
        help_mechanisms = []

        # Detect contact information
        help_selectors = [
            # Contact links/info
            "a[href^='mailto:']",
            "a[href^='tel:']",
            "a[href*='contact']",
            "[class*='contact']",
            "[id*='contact']",
            # Help links
            "a[href*='help']",
            "a[href*='support']",
            "a[href*='faq']",
            "[class*='help']",
            "[id*='help']",
            "[class*='support']",
            "[id*='support']",
            "[class*='faq']",
            "[id*='faq']",
            # Chat/automated assistance
            "[class*='chat']",
            "[id*='chat']",
            "[class*='bot']",
            "[id*='bot']",
            "[aria-label*='chat']",
            "[aria-label*='help']",
            "[aria-label*='support']"
        ]

        help_elements = self.driver.find_elements(By.CSS_SELECTOR, ", ".join(help_selectors))

        # Process found elements
        for element in help_elements:
            try:
                element_text = element.text.strip() if element.text else ""
                element_href = element.get_attribute("href") or ""
                element_aria_label = element.get_attribute("aria-label") or ""

                # Determine help type
                help_type = None
                if element_href.startswith("mailto:"):
                    help_type = "contact_email"
                elif element_href.startswith("tel:"):
                    help_type = "contact_phone"
                elif "chat" in element_text.lower() or "chat" in element_aria_label.lower():
                    help_type = "automated_chat"
                elif "faq" in element_text.lower() or "faq" in element_href.lower():
                    help_type = "self_help"
                elif "help" in element_text.lower() or "help" in element_href.lower():
                    help_type = "help_page"
                elif "contact" in element_text.lower() or "contact" in element_href.lower():
                    help_type = "contact_page"
                else:
                    help_type = "unknown_help"

                # Get position information
                position = self.driver.execute_script("""
                    var el = arguments[0];
                    var rect = el.getBoundingClientRect();
                    var bodyRect = document.body.getBoundingClientRect();

                    return {
                        top: rect.top - bodyRect.top,
                        left: rect.left - bodyRect.left,
                        bottom: rect.bottom - bodyRect.top,
                        right: rect.right - bodyRect.left
                    };
                """, element)

                help_mechanisms.append({
                    "element": element.tag_name,
                    "element_info": {
                        "id": element.get_attribute("id"),
                        "class": element.get_attribute("class"),
                        "href": element_href,
                        "text": element_text,
                        "aria_label": element_aria_label
                    },
                    "help_type": help_type,
                    "position": position
                })

            except Exception as e:
                self.logger.error(f"Error processing help element {element.tag_name}: {str(e)}")

        return help_mechanisms

    def _test_3_3_7_accessible_authentication(self):
        """
        Test for WCAG 2.2 Success Criterion 3.3.7: Accessible Authentication.

        For authentication process steps, at least one method doesn't rely on a cognitive function test.
        """
        self.logger.info("Testing 3.3.7: Accessible Authentication")

        criterion_results = {
            "criterion": "3.3.7",
            "name": self.wcag22_criteria["3.3.7"]["name"],
            "level": self.wcag22_criteria["3.3.7"]["level"],
            "description": self.wcag22_criteria["3.3.7"]["description"],
            "issues": [],
            "passed": True
        }

        # Look for authentication forms/components
        auth_selectors = [
            "form[action*='login']",
            "form[action*='signin']",
            "form[action*='auth']",
            "form[id*='login']",
            "form[id*='signin']",
            "form[class*='login']",
            "form[class*='signin']",
            "[id*='login']",
            "[id*='signin']",
            "[class*='login']",
            "[class*='signin']"
        ]

        auth_elements = self.driver.find_elements(By.CSS_SELECTOR, ", ".join(auth_selectors))

        if not auth_elements:
            criterion_results["summary"] = "No authentication forms detected on the page"
            return criterion_results

        # Look for potential cognitive function tests
        for auth_element in auth_elements:
            try:
                # Look for CAPTCHAs
                captcha_elements = auth_element.find_elements(By.CSS_SELECTOR,
                                                              "[class*='captcha'], [id*='captcha'], [class*='recaptcha'], [id*='recaptcha'], iframe[src*='recaptcha'], iframe[src*='captcha']")

                # Look for password complexity requirements
                password_fields = auth_element.find_elements(By.CSS_SELECTOR, "input[type='password']")
                password_complexity_indicators = auth_element.find_elements(By.CSS_SELECTOR,
                                                                            "[class*='password-strength'], [id*='password-strength'], [class*='complexity'], [id*='complexity']")

                # Look for alternative authentication methods
                alternative_methods = auth_element.find_elements(By.CSS_SELECTOR,
                                                                 "button[class*='sso'], a[class*='sso'], button[class*='google'], a[class*='google'], button[class*='facebook'], a[class*='facebook']")

                # Look for authentication without cognitive function tests
                webauthn_elements = auth_element.find_elements(By.CSS_SELECTOR,
                                                               "[class*='webauthn'], [id*='webauthn'], [class*='fingerprint'], [id*='fingerprint'], [class*='biometric'], [id*='biometric']")

                # Determine if cognitive function tests are being used
                has_cognitive_tests = len(captcha_elements) > 0
                has_alternatives = len(alternative_methods) > 0 or len(webauthn_elements) > 0

                if has_cognitive_tests and not has_alternatives:
                    criterion_results["issues"].append({
                        "element": auth_element.tag_name,
                        "element_info": {
                            "id": auth_element.get_attribute("id"),
                            "class": auth_element.get_attribute("class")
                        },
                        "cognitive_tests": {
                            "captcha": len(captcha_elements) > 0,
                            "password_complexity": len(password_complexity_indicators) > 0
                        },
                        "alternatives": {
                            "sso_or_social": len(alternative_methods) > 0,
                            "webauthn_or_biometric": len(webauthn_elements) > 0
                        },
                        "message": "Authentication form uses cognitive function tests without alternatives"
                    })
                    criterion_results["passed"] = False

            except Exception as e:
                self.logger.error(f"Error testing authentication form: {str(e)}")

        if criterion_results["passed"]:
            criterion_results["summary"] = "All authentication forms provide alternatives to cognitive function tests"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} authentication forms without alternatives to cognitive function tests"

        # Note: This test is limited to what can be automatically detected
        criterion_results["manual_check_required"] = True
        criterion_results["manual_check_instructions"] = (
            "Automatic detection of cognitive function tests in authentication is limited. "
            "Manually verify if authentication processes that use CAPTCHAs, memory of complex passwords, "
            "or other cognitive tests offer alternatives like WebAuthn, SSO, or other accessible methods."
        )

        return criterion_results

    def _test_3_3_9_redundant_entry(self):
        """
        Test for WCAG 2.2 Success Criterion 3.3.9: Redundant Entry.

        Information previously entered by or provided to the user that is required
        to be entered again is auto-populated, or available for the user to select.
        """
        self.logger.info("Testing 3.3.9: Redundant Entry")

        criterion_results = {
            "criterion": "3.3.9",
            "name": self.wcag22_criteria["3.3.9"]["name"],
            "level": self.wcag22_criteria["3.3.9"]["level"],
            "description": self.wcag22_criteria["3.3.9"]["description"],
            "issues": [],
            "passed": True
        }

        # Find multi-step forms or possible redundant entry situations
        multi_step_indicators = self.driver.find_elements(By.CSS_SELECTOR,
                                                          "[class*='steps'], [id*='steps'], [class*='wizard'], [id*='wizard'], [class*='multi-step'], [id*='multi-step']")

        # Look for forms with similar field types that might indicate redundant entry
        forms = self.driver.find_elements(By.TAG_NAME, "form")

        # If no forms or multi-step indicators are found, this criterion might not apply
        if not forms and not multi_step_indicators:
            criterion_results["summary"] = "No multi-step forms or potential redundant entry situations detected"
            criterion_results["not_applicable"] = True
            return criterion_results

        # Check for common patterns of redundant entry
        redundant_entry_patterns = [
            {
                "field_types": ["email", "email"],
                "message": "Email confirmation field without auto-population"
            },
            {
                "field_types": ["password", "password"],
                "message": "Password confirmation field without auto-population"
            },
            {
                "field_types": ["address", "address"],
                "message": "Multiple address fields that might require redundant entry"
            }
        ]

        for form in forms:
            try:
                # Get input fields in the form
                input_fields = form.find_elements(By.TAG_NAME, "input")

                # Extract field types and attributes
                field_info = []
                for field in input_fields:
                    field_type = field.get_attribute("type")
                    field_name = field.get_attribute("name")
                    field_id = field.get_attribute("id")
                    field_autocomplete = field.get_attribute("autocomplete")
                    field_info.append({
                        "type": field_type,
                        "name": field_name,
                        "id": field_id,
                        "autocomplete": field_autocomplete
                    })

                # Look for potential redundant entry based on field names and types
                for i, field1 in enumerate(field_info):
                    for j, field2 in enumerate(field_info[i + 1:], i + 1):
                        # Check for confirmation fields (common redundant entry pattern)
                        is_confirmation_pair = (
                                field1["name"] and field2["name"] and
                                (field1["name"] in field2["name"] or field2["name"] in field1["name"]) and
                                field1["type"] == field2["type"]
                        )

                        # Check if autocomplete is disabled
                        autocomplete_disabled = (
                                field2["autocomplete"] == "off" or
                                input_fields[j].get_attribute("readonly") is not None
                        )

                        if is_confirmation_pair and autocomplete_disabled:
                            criterion_results["issues"].append({
                                "element": "form",
                                "element_info": {
                                    "id": form.get_attribute("id"),
                                    "class": form.get_attribute("class")
                                },
                                "fields": [
                                    {
                                        "type": field1["type"],
                                        "name": field1["name"],
                                        "id": field1["id"]
                                    },
                                    {
                                        "type": field2["type"],
                                        "name": field2["name"],
                                        "id": field2["id"],
                                        "autocomplete": field2["autocomplete"]
                                    }
                                ],
                                "message": f"Potential redundant entry for {field1['type']} fields without autocomplete support"
                            })
                            criterion_results["passed"] = False

            except Exception as e:
                self.logger.error(f"Error testing form for redundant entry: {str(e)}")

        if criterion_results["passed"]:
            criterion_results["summary"] = "No clear redundant entry issues detected"
        else:
            criterion_results["summary"] = f"Found {len(criterion_results['issues'])} potential redundant entry issues"

        # Note that this test has limitations
        criterion_results["manual_check_required"] = True
        criterion_results["manual_check_instructions"] = (
            "Automatic detection of redundant entry is limited. Manually verify if previously entered "
            "information that is requested again is auto-populated or available for selection."
        )

        return criterion_results

    def _create_summary(self, results):
        """Create a summary of all test results."""
        summary = {
            "total_issues": 0,
            "criteria_tested": len(results),
            "criteria_passed": 0,
            "criteria_failed": 0,
            "manual_checks_required": 0
        }

        # Process results for each criterion
        for criterion_id, criterion_results in results.items():
            if criterion_results.get("passed", True):
                summary["criteria_passed"] += 1
            else:
                summary["criteria_failed"] += 1
                summary["total_issues"] += len(criterion_results.get("issues", []))

            if criterion_results.get("manual_check_required", False):
                summary["manual_checks_required"] += 1

        return summary

    def generate_report(self, results, output_dir):
        """Generate report from test results."""
        try:
            # Generate filenames
            page_id = results['url'].replace('https://', '').replace('http://', '').replace('/', '_')
            json_filename = f"wcag22_{page_id}_{results['timestamp']}.json"
            html_filename = f"wcag22_{page_id}_{results['timestamp']}.html"

            # Save JSON report
            json_path = os.path.join(output_dir, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            # Generate and save HTML report
            html_report = generate_html_report(results)
            html_path = os.path.join(output_dir, html_filename)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_report)

            return {
                'json': json_path,
                'html': html_path
            }

        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return None

    def _parse_pixel_value(self, value):
        """Parse a CSS pixel value string and return a float."""
        if not value or not isinstance(value, str):
            return 0

        try:
            return float(value.replace('px', ''))
        except (ValueError, TypeError):
            return 0

    def _test_2_4_7_focus_visible(self):
        """
        Test for WCAG 2.2 Success Criterion 2.4.7: Focus Visible (AA).

        When any user interface component receives keyboard focus,
        there is a visible indication of focus.
        """
        self.logger.info("Testing 2.4.7: Focus Visible (AA)")

        criterion_results = {
            "criterion": "2.4.7",
            "name": "Focus Visible",
            "level": "AA",
            "description": "Any keyboard operable user interface has a mode of operation where the keyboard focus indicator is visible.",
            "issues": [],
            "passed": True
        }

        try:
            # Get all focusable elements
            focusable_selectors = [
                "a", "button", "input", "select", "textarea",
                "[tabindex]:not([tabindex='-1'])", "[role='button']",
                "[role='link']", "[role='checkbox']", "[role='radio']",
                "[role='tab']", "[role='menuitem']"
            ]

            selector_string = ", ".join(focusable_selectors)
            focusable_elements = self.driver.find_elements(By.CSS_SELECTOR, selector_string)

            self.logger.info(f"Found {len(focusable_elements)} focusable elements")

            # Test each element (max 50 to avoid timeouts)
            for element in focusable_elements[:50]:
                try:
                    # Get element info for reporting
                    element_info = {
                        "tag": element.tag_name,
                        "id": element.get_attribute("id") or "",
                        "class": element.get_attribute("class") or "",
                        "text": (element.text[:30] + "...") if len(element.text or "") > 30 else (
                                    element.text or "[No text]")
                    }

                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.1)  # Brief pause

                    # Get unfocused styles
                    unfocused_styles = self.driver.execute_script("""
                        var el = arguments[0];
                        var style = window.getComputedStyle(el);
                        return {
                            outlineWidth: style.outlineWidth,
                            outlineStyle: style.outlineStyle,
                            outlineColor: style.outlineColor,
                            boxShadow: style.boxShadow,
                            borderWidth: style.borderWidth,
                            borderStyle: style.borderStyle,
                            borderColor: style.borderColor,
                            backgroundColor: style.backgroundColor
                        };
                    """, element)

                    # Focus the element
                    self.driver.execute_script("arguments[0].focus();", element)
                    time.sleep(0.1)  # Brief pause for focus styles to apply

                    # Get focused styles
                    focused_styles = self.driver.execute_script("""
                        var el = arguments[0];
                        var style = window.getComputedStyle(el);
                        return {
                            outlineWidth: style.outlineWidth,
                            outlineStyle: style.outlineStyle,
                            outlineColor: style.outlineColor,
                            boxShadow: style.boxShadow,
                            borderWidth: style.borderWidth,
                            borderStyle: style.borderStyle,
                            borderColor: style.borderColor,
                            backgroundColor: style.backgroundColor
                        };
                    """, element)

                    # Check if there's a visible focus indicator
                    # For AA level, any visible indication is sufficient
                    outline_visible = (
                            focused_styles.get("outlineStyle") != "none" and
                            focused_styles.get("outlineStyle") != unfocused_styles.get("outlineStyle")
                    )

                    box_shadow_visible = (
                            focused_styles.get("boxShadow") != "none" and
                            focused_styles.get("boxShadow") != unfocused_styles.get("boxShadow")
                    )

                    border_visible = (
                            focused_styles.get("borderStyle") != "none" and
                            (focused_styles.get("borderColor") != unfocused_styles.get("borderColor") or
                             focused_styles.get("borderWidth") != unfocused_styles.get("borderWidth") or
                             focused_styles.get("borderStyle") != unfocused_styles.get("borderStyle"))
                    )

                    background_change = (
                            focused_styles.get("backgroundColor") != unfocused_styles.get("backgroundColor")
                    )

                    has_visible_focus = outline_visible or box_shadow_visible or border_visible or background_change

                    if not has_visible_focus:
                        criterion_results["issues"].append({
                            "element": element_info["tag"],
                            "element_info": element_info,
                            "message": "Element has no visible focus indicator",
                            "unfocused_styles": unfocused_styles,
                            "focused_styles": focused_styles
                        })
                        criterion_results["passed"] = False

                        # Take screenshot for evidence
                        screenshot_path = os.path.join(self.output_dir,
                                                       f"focus_issue_{len(criterion_results['issues'])}.png")
                        self.driver.save_screenshot(screenshot_path)

                except Exception as e:
                    self.logger.error(f"Error testing focus visibility for element {element.tag_name}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error in focus visibility test: {str(e)}")
            criterion_results["error"] = str(e)

        if criterion_results["passed"]:
            criterion_results["summary"] = "All focusable elements have visible focus indicators"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} elements with no visible focus indicators"

        return criterion_results

    def _test_1_4_11_non_text_contrast(self):
        """
        Test for WCAG 2.2 Success Criterion 1.4.11: Non-text Contrast (AA).

        Visual presentation of UI components and graphical objects
        has a contrast ratio of at least 3:1 against adjacent colors.
        """
        self.logger.info("Testing 1.4.11: Non-text Contrast")

        criterion_results = {
            "criterion": "1.4.11",
            "name": "Non-text Contrast",
            "level": "AA",
            "description": "The visual presentation of UI components and graphical objects has a contrast ratio of at least 3:1 against adjacent colors.",
            "issues": [],
            "passed": True
        }

        try:
            # Define selectors for UI components to test
            ui_components_selectors = [
                # Form controls
                "input[type='checkbox']", "input[type='radio']", "input[type='range']",
                "input[type='text']", "input[type='password']", "input[type='email']",
                "input[type='tel']", "input[type='number']", "input[type='search']",
                "input[type='submit']", "input[type='reset']", "input[type='button']",
                "textarea", "select",

                # Custom controls and interactive components
                "button", "a.button", "a[role='button']",
                "[role='checkbox']", "[role='radio']", "[role='slider']",
                "[role='switch']", "[role='tab']", "details summary",

                # Navigation and other UI components
                ".pagination a", ".nav a", "footer a",
                ".menu-item", ".dropdown", ".accordion",

                # Icons and graphical UI elements
                "svg", "svg *", "i.icon", ".icon", "[class*='icon']"
            ]

            # Combine selectors and find elements
            selector_string = ", ".join(ui_components_selectors)
            ui_elements = self.driver.find_elements(By.CSS_SELECTOR, selector_string)

            self.logger.info(f"Found {len(ui_elements)} UI components to test")

            # Test each UI component for contrast (max 50 to avoid timeouts)
            for element in ui_elements[:50]:
                try:
                    # Get element info for reporting
                    element_info = {
                        "tag": element.tag_name,
                        "id": element.get_attribute("id") or "",
                        "class": element.get_attribute("class") or "",
                        "role": element.get_attribute("role") or "",
                        "type": element.get_attribute("type") or ""
                    }

                    # Scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.1)  # Brief pause

                    # Run contrast analysis using JavaScript
                    contrast_data = self.driver.execute_script("""
                        function getColor(colorStr) {
                            // Handle rgba and rgb format
                            var rgbMatch = colorStr.match(/rgba?\\s*\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*(?:,\\s*([\\d.]+)\\s*)?\\)/i);
                            if (rgbMatch) {
                                return {
                                    r: parseInt(rgbMatch[1], 10),
                                    g: parseInt(rgbMatch[2], 10),
                                    b: parseInt(rgbMatch[3], 10),
                                    a: rgbMatch[4] ? parseFloat(rgbMatch[4]) : 1
                                };
                            }

                            // Handle hex format
                            var hexMatch = colorStr.match(/#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/i);
                            if (hexMatch) {
                                return {
                                    r: parseInt(hexMatch[1], 16),
                                    g: parseInt(hexMatch[2], 16),
                                    b: parseInt(hexMatch[3], 16),
                                    a: 1
                                };
                            }

                            // Handle shorthand hex format
                            var shortHexMatch = colorStr.match(/#([0-9a-f])([0-9a-f])([0-9a-f])/i);
                            if (shortHexMatch) {
                                return {
                                    r: parseInt(shortHexMatch[1] + shortHexMatch[1], 16),
                                    g: parseInt(shortHexMatch[2] + shortHexMatch[2], 16),
                                    b: parseInt(shortHexMatch[3] + shortHexMatch[3], 16),
                                    a: 1
                                };
                            }

                            // Handle named colors by creating a temporary element
                            var tempEl = document.createElement('div');
                            tempEl.style.color = colorStr;
                            document.body.appendChild(tempEl);
                            var computedColor = getComputedStyle(tempEl).color;
                            document.body.removeChild(tempEl);

                            // Parse the computed color (should be in rgb/rgba format)
                            return getColor(computedColor);
                        }

                        function luminance(r, g, b) {
                            // Convert RGB to relative luminance
                            var a = [r, g, b].map(function (v) {
                                v /= 255;
                                return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
                            });
                            return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
                        }

                        function contrastRatio(color1, color2) {
                            // Calculate contrast ratio
                            var l1 = luminance(color1.r, color1.g, color1.b);
                            var l2 = luminance(color2.r, color2.g, color2.b);
                            return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
                        }

                        var element = arguments[0];
                        var elementStyle = window.getComputedStyle(element);
                        var boundingBox = element.getBoundingClientRect();

                        var data = {
                            elementColor: elementStyle.backgroundColor,
                            borderColor: elementStyle.borderColor,
                            elementSize: {
                                width: boundingBox.width,
                                height: boundingBox.height
                            },
                            issues: []
                        };

                        // Get parent color (for background)
                        var parent = element.parentElement;
                        var parentBgColor = 'white'; // Default in case we can't get it

                        while (parent) {
                            var parentStyle = window.getComputedStyle(parent);
                            if (parentStyle.backgroundColor && parentStyle.backgroundColor !== 'rgba(0, 0, 0, 0)') {
                                parentBgColor = parentStyle.backgroundColor;
                                break;
                            }
                            parent = parent.parentElement;
                        }

                        data.parentColor = parentBgColor;

                        // Get element RGB color
                        var elementRgb = getColor(elementStyle.backgroundColor);

                        // If background is transparent, use parent bg
                        if (elementRgb.a < 0.1) {
                            elementRgb = getColor(parentBgColor);
                        }

                        // Check border contrast if there's a border
                        if (elementStyle.borderStyle !== 'none' && elementStyle.borderWidth !== '0px') {
                            var borderRgb = getColor(elementStyle.borderColor);
                            var borderContrast = contrastRatio(elementRgb, borderRgb);

                            data.borderContrast = borderContrast;

                            if (borderContrast < 3) {
                                data.issues.push({
                                    type: 'border_contrast',
                                    contrast: borderContrast,
                                    elementColor: elementStyle.backgroundColor,
                                    borderColor: elementStyle.borderColor,
                                    message: 'Border contrast ratio is less than 3:1'
                                });
                            }
                        }

                        // For form controls, check against parent background
                        if (element.tagName === 'INPUT' || element.tagName === 'SELECT' || 
                            element.tagName === 'TEXTAREA' || element.tagName === 'BUTTON' ||
                            element.getAttribute('role') === 'button' || 
                            element.getAttribute('role') === 'checkbox' ||
                            element.getAttribute('role') === 'radio') {

                            var parentRgb = getColor(parentBgColor);
                            var controlContrast = contrastRatio(elementRgb, parentRgb);

                            data.controlContrast = controlContrast;

                            if (controlContrast < 3) {
                                data.issues.push({
                                    type: 'control_contrast',
                                    contrast: controlContrast,
                                    controlColor: elementStyle.backgroundColor,
                                    parentColor: parentBgColor,
                                    message: 'Form control contrast ratio is less than 3:1'
                                });
                            }
                        }

                        // For icons (SVG, i.icon, etc.)
                        if (element.tagName === 'SVG' || 
                            (element.className && element.className.includes('icon'))) {

                            var fillColor = elementStyle.fill;
                            var strokeColor = elementStyle.stroke;

                            // If these are 'none' or not set, try color
                            if (fillColor === 'none' || !fillColor) {
                                fillColor = elementStyle.color;
                            }

                            var iconRgb = getColor(fillColor);
                            var parentRgb = getColor(parentBgColor);
                            var iconContrast = contrastRatio(iconRgb, parentRgb);

                            data.iconContrast = iconContrast;

                            if (iconContrast < 3) {
                                data.issues.push({
                                    type: 'icon_contrast',
                                    contrast: iconContrast, 
                                    iconColor: fillColor,
                                    parentColor: parentBgColor,
                                    message: 'Icon contrast ratio is less than 3:1'
                                });
                            }
                        }

                        return data;
                    """, element)

                    # Process contrast data
                    if contrast_data and 'issues' in contrast_data and contrast_data['issues']:
                        for issue in contrast_data['issues']:
                            criterion_results["issues"].append({
                                "element": element_info["tag"],
                                "element_info": element_info,
                                "message": issue['message'],
                                "contrast_ratio": issue.get('contrast', 'unknown'),
                                "colors": {
                                    "element": issue.get('elementColor',
                                                         issue.get('controlColor', issue.get('iconColor', 'unknown'))),
                                    "adjacent": issue.get('borderColor', issue.get('parentColor', 'unknown'))
                                }
                            })
                            criterion_results["passed"] = False

                            # Take screenshot for evidence
                            screenshot_path = os.path.join(self.output_dir,
                                                           f"contrast_issue_{len(criterion_results['issues'])}.png")
                            self.driver.save_screenshot(screenshot_path)

                except Exception as e:
                    self.logger.error(f"Error testing non-text contrast for element {element.tag_name}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error in non-text contrast test: {str(e)}")
            criterion_results["error"] = str(e)

        if criterion_results["passed"]:
            criterion_results["summary"] = "All UI components meet 3:1 contrast ratio requirement"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} UI components with insufficient contrast"

        return criterion_results

    def _test_1_4_12_text_spacing(self):
        """
        Test for WCAG 2.2 Success Criterion 1.4.12: Text Spacing.

        In content implemented using markup languages, no loss of content or functionality
        occurs when settings are changed for line height, paragraph spacing, letter spacing,
        and word spacing.
        """
        self.logger.info("Testing 1.4.12: Text Spacing")

        criterion_results = {
            "criterion": "1.4.12",
            "name": "Text Spacing",
            "level": "AA",
            "description": "No loss of content or functionality occurs when text spacing is adjusted.",
            "issues": [],
            "passed": True
        }

        try:
            # Save the original page dimensions
            original_dimensions = self.driver.execute_script("""
                return {
                    width: document.documentElement.scrollWidth,
                    height: document.documentElement.scrollHeight,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                };
            """)

            # Inject the text spacing stylesheet
            self.driver.execute_script("""
                // Create style element
                var style = document.createElement('style');
                style.id = 'text-spacing-test';
                style.textContent = `
                    * {
                        line-height: 1.5 !important;
                        letter-spacing: 0.12em !important;
                        word-spacing: 0.16em !important;
                    }
                    p, li, h1, h2, h3, h4, h5, h6, dl, dd, blockquote, figcaption {
                        margin-bottom: 2em !important;
                    }
                `;
                document.head.appendChild(style);
            """)

            # Wait for the page to adjust to the new styles
            time.sleep(1)

            # Get the new dimensions after text spacing adjustments
            new_dimensions = self.driver.execute_script("""
                return {
                    width: document.documentElement.scrollWidth,
                    height: document.documentElement.scrollHeight,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                };
            """)

            # Capture page screenshots before checking for issues (for evidence)
            screenshot_path = os.path.join(self.output_dir, "text_spacing_test.png")
            self.driver.save_screenshot(screenshot_path)

            # Look for content overflow issues
            overflow_issues = self.driver.execute_script("""
                var issues = [];
                var viewport_width = window.innerWidth;

                // Function to get computed style
                function getStyle(element, prop) {
                    return window.getComputedStyle(element).getPropertyValue(prop);
                }

                // Check if an element's content is clipped or overflowing
                function checkOverflow(element) {
                    var rect = element.getBoundingClientRect();

                    // Skip elements not in viewport
                    if (rect.right < 0 || rect.bottom < 0 || 
                        rect.left > window.innerWidth || rect.top > window.innerHeight) {
                        return null;
                    }

                    var style = window.getComputedStyle(element);

                    // Get overflow settings
                    var overflowX = style.overflowX;
                    var overflowY = style.overflowY;
                    var overflow = style.overflow;

                    // Check width vs scrollWidth for horizontal overflow
                    var hasHorizontalOverflow = element.scrollWidth > element.clientWidth;

                    // Check if overflow is hidden and content extends beyond boundaries
                    var isClipped = (overflow === 'hidden' || overflowX === 'hidden') && hasHorizontalOverflow;

                    if (isClipped) {
                        return {
                            element: element.tagName.toLowerCase(),
                            id: element.id || null,
                            class: element.className || null,
                            text: element.textContent.substring(0, 50) + (element.textContent.length > 50 ? '...' : ''),
                            overflow: {
                                clientWidth: element.clientWidth,
                                scrollWidth: element.scrollWidth,
                                overflowX: overflowX,
                                overflowY: overflowY
                            }
                        };
                    }

                    return null;
                }

                // Get all text containers
                var textContainers = document.querySelectorAll(
                    'p, h1, h2, h3, h4, h5, h6, li, td, th, dt, dd, figcaption, blockquote, article, section, nav, ' +
                    'div:not(:empty), span:not(:empty)'
                );

                // Check each container for overflow
                textContainers.forEach(function(container) {
                    var issue = checkOverflow(container);
                    if (issue) {
                        issues.push(issue);
                    }
                });

                return issues;
            """)

            # Check for elements that disappear when text spacing is applied
            hidden_elements = self.driver.execute_script("""
                // Find all potentially impacted text elements (excluding SVG/images/etc.)
                var before = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, a, button, span:not(:empty), div:not(:empty)');
                var visibleBefore = Array.from(before).filter(el => 
                    el.offsetWidth > 0 && 
                    el.offsetHeight > 0 && 
                    window.getComputedStyle(el).display !== 'none' && 
                    window.getComputedStyle(el).visibility !== 'hidden'
                );

                // Extract identifiable information
                return visibleBefore.filter(el => {
                    // Check if still visible
                    return (
                        el.offsetWidth === 0 || 
                        el.offsetHeight === 0 || 
                        window.getComputedStyle(el).display === 'none' || 
                        window.getComputedStyle(el).visibility === 'hidden'
                    );
                }).map(el => {
                    return {
                        element: el.tagName.toLowerCase(),
                        id: el.id || null,
                        class: el.className || null,
                        text: el.textContent.trim().substring(0, 50) + (el.textContent.length > 50 ? '...' : '')
                    };
                });
            """)

            # Check for layout shifts that indicate content might be lost
            layout_issues = self.driver.execute_script("""
                // Check for negative margins, absolute positioning, and other potential issues
                var issues = [];

                // Get all elements with text
                var elements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, a, button, span:not(:empty), div:not(:empty)');

                elements.forEach(function(el) {
                    var style = window.getComputedStyle(el);

                    // Check for negative margins
                    if (parseFloat(style.marginLeft) < 0 || 
                        parseFloat(style.marginRight) < 0 || 
                        parseFloat(style.marginTop) < 0 || 
                        parseFloat(style.marginBottom) < 0) {

                        issues.push({
                            element: el.tagName.toLowerCase(),
                            id: el.id || null,
                            class: el.className || null,
                            text: el.textContent.trim().substring(0, 50) + (el.textContent.length > 50 ? '...' : ''),
                            issue: 'negative_margin',
                            style: {
                                marginLeft: style.marginLeft,
                                marginRight: style.marginRight,
                                marginTop: style.marginTop,
                                marginBottom: style.marginBottom
                            }
                        });
                    }

                    // Check for fixed widths that might cause overflow
                    if (style.width !== 'auto' && style.width !== '' && !style.width.includes('%') && 
                        style.maxWidth !== 'none' && style.overflow === 'hidden') {

                        issues.push({
                            element: el.tagName.toLowerCase(),
                            id: el.id || null,
                            class: el.className || null,
                            text: el.textContent.trim().substring(0, 50) + (el.textContent.length > 50 ? '...' : ''),
                            issue: 'fixed_width_with_hidden_overflow',
                            style: {
                                width: style.width,
                                maxWidth: style.maxWidth,
                                overflow: style.overflow
                            }
                        });
                    }
                });

                return issues;
            """)

            # Record the number and types of issues
            if overflow_issues:
                for issue in overflow_issues:
                    criterion_results["issues"].append({
                        "element": issue["element"],
                        "element_info": {
                            "id": issue["id"],
                            "class": issue["class"],
                            "text": issue["text"]
                        },
                        "issue_type": "overflow",
                        "message": "Element content overflows and is clipped when text spacing is adjusted",
                        "details": issue["overflow"]
                    })
                    criterion_results["passed"] = False

            if hidden_elements:
                for element in hidden_elements:
                    criterion_results["issues"].append({
                        "element": element["element"],
                        "element_info": {
                            "id": element["id"],
                            "class": element["class"],
                            "text": element["text"]
                        },
                        "issue_type": "hidden",
                        "message": "Element becomes hidden when text spacing is adjusted"
                    })
                    criterion_results["passed"] = False

            if layout_issues:
                for issue in layout_issues:
                    criterion_results["issues"].append({
                        "element": issue["element"],
                        "element_info": {
                            "id": issue["id"],
                            "class": issue["class"],
                            "text": issue["text"]
                        },
                        "issue_type": issue["issue"],
                        "message": "Element has layout properties that may cause content loss with adjusted text spacing",
                        "details": issue["style"]
                    })
                    criterion_results["passed"] = False

            # Include dimension changes in the report
            criterion_results["dimensions"] = {
                "original": original_dimensions,
                "adjusted": new_dimensions,
                "changes": {
                    "width": new_dimensions["width"] - original_dimensions["width"],
                    "height": new_dimensions["height"] - original_dimensions["height"]
                }
            }

            # Remove the injected stylesheet to restore original appearance
            self.driver.execute_script("""
                var styleElement = document.getElementById('text-spacing-test');
                if (styleElement) {
                    styleElement.parentNode.removeChild(styleElement);
                }
            """)

        except Exception as e:
            self.logger.error(f"Error in text spacing test: {str(e)}")
            criterion_results["error"] = str(e)

        if criterion_results["passed"]:
            criterion_results["summary"] = "No loss of content or functionality observed when text spacing is adjusted"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} issues with text spacing adjustments"

        return criterion_results

    def _test_2_5_7_dragging_movements_enhanced(self):
        """
        Enhanced test for WCAG 2.2 Success Criterion 2.5.7: Dragging Movements.

        All functionality that uses a dragging movement can be operated by a single pointer
        without dragging, unless dragging is essential.

        This enhanced version uses Selenium actions to actually test drag functionality.
        """
        self.logger.info("Testing 2.5.7: Dragging Movements (Enhanced)")

        criterion_results = {
            "criterion": "2.5.7",
            "name": "Dragging Movements",
            "level": "AA",
            "description": "All functionality that uses a dragging movement can be operated by a single pointer without dragging, unless dragging is essential.",
            "issues": [],
            "passed": True
        }

        try:
            # Find potential draggable elements
            draggable_selectors = [
                # Explicit draggable elements
                "[draggable='true']",
                # Common draggable components
                ".draggable", ".ui-draggable", ".drag", "[aria-grabbed]",
                # Sliders
                "input[type='range']", ".slider", "[role='slider']",
                # Common libraries
                ".ui-slider", ".ui-sortable", ".sortable", ".react-draggable",
                # Elements with drag styles or attributes
                "[class*='drag']", "[id*='drag']", "[class*='slider']", "[id*='slider']"
            ]

            selector_string = ", ".join(draggable_selectors)
            draggable_elements = self.driver.find_elements(By.CSS_SELECTOR, selector_string)

            self.logger.info(f"Found {len(draggable_elements)} potentially draggable elements")

            # Test each draggable element (limited to first 20 to prevent test from running too long)
            for element in draggable_elements[:20]:
                # Get element info for reporting
                element_info = {
                    "tag": element.tag_name,
                    "id": element.get_attribute("id") or "",
                    "class": element.get_attribute("class") or "",
                    "draggable": element.get_attribute("draggable") or "",
                    "role": element.get_attribute("role") or ""
                }

                # Attempt to test if this element is actually draggable
                is_draggable, drag_test_results = self._test_element_draggability(element)

                if is_draggable:
                    # Test if there are alternatives to dragging
                    has_alternatives, alternatives = self._find_dragging_alternatives(element)

                    if not has_alternatives:
                        criterion_results["issues"].append({
                            "element": element_info["tag"],
                            "element_info": element_info,
                            "drag_test_results": drag_test_results,
                            "message": "Draggable element without detected alternative non-dragging mechanism"
                        })
                        criterion_results["passed"] = False

                        # Take screenshot for evidence
                        screenshot_path = os.path.join(self.output_dir,
                                                       f"drag_issue_{len(criterion_results['issues'])}.png")
                        self.driver.save_screenshot(screenshot_path)
                    else:
                        # Include information about the alternatives found
                        self.logger.info(f"Found dragging alternatives for {element_info['tag']}: {alternatives}")

        except Exception as e:
            self.logger.error(f"Error in dragging movements test: {str(e)}")
            criterion_results["error"] = str(e)

        if criterion_results["passed"]:
            criterion_results["summary"] = "All draggable elements have alternative non-dragging mechanisms"
        else:
            criterion_results[
                "summary"] = f"Found {len(criterion_results['issues'])} elements with dragging functionality without alternatives"

        return criterion_results

    def _test_element_draggability(self, element):
        """
        Test if an element is actually draggable using Selenium Actions.

        Args:
            element: WebElement to test

        Returns:
            tuple: (is_draggable, drag_test_results)
        """
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.2)

            # Get initial position
            initial_location = element.location

            # For sliders, use a different approach
            if element.tag_name == "input" and element.get_attribute("type") == "range":
                # This is a range input slider
                actions = ActionChains(self.driver)
                actions.click_and_hold(element).move_by_offset(20, 0).release().perform()

                # Check if value changed
                new_value = element.get_attribute("value")
                initial_value = element.get_attribute("defaultValue") or "0"

                return new_value != initial_value, {
                    "element_type": "range_slider",
                    "initial_value": initial_value,
                    "new_value": new_value
                }

            # For standard draggable elements
            actions = ActionChains(self.driver)
            actions.click_and_hold(element).move_by_offset(10, 10).release().perform()

            # Get new position
            time.sleep(0.5)  # Wait for any animations to complete
            final_location = element.location

            # Check if position changed
            position_changed = (
                    abs(final_location['x'] - initial_location['x']) > 5 or
                    abs(final_location['y'] - initial_location['y']) > 5
            )

            # For elements with draggable attribute, consider them draggable even if test doesn't move them
            is_explicitly_draggable = element.get_attribute("draggable") == "true"

            is_draggable = position_changed or is_explicitly_draggable

            return is_draggable, {
                "initial_location": initial_location,
                "final_location": final_location,
                "position_changed": position_changed,
                "explicitly_draggable": is_explicitly_draggable
            }

        except Exception as e:
            self.logger.error(f"Error testing element draggability: {str(e)}")
            return False, {"error": str(e)}

    def _find_dragging_alternatives(self, draggable_element):
        """
        Find alternative mechanisms for dragging functionality.

        Args:
            draggable_element: The draggable WebElement

        Returns:
            tuple: (has_alternatives, alternatives_info)
        """
        alternatives = []

        try:
            # Get element information
            element_id = draggable_element.get_attribute("id")
            element_tag = draggable_element.tag_name
            element_role = draggable_element.get_attribute("role")

            # 1. Check for common slider alternatives
            if element_tag == "input" and draggable_element.get_attribute("type") == "range":
                # Look for text inputs with same name
                input_name = draggable_element.get_attribute("name")
                if input_name:
                    text_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                                                            f"input[type='number'][name='{input_name}'], input[type='text'][name='{input_name}']")
                    if text_inputs:
                        alternatives.append({
                            "type": "text_input",
                            "element_tag": text_inputs[0].tag_name,
                            "element_id": text_inputs[0].get_attribute("id") or ""
                        })

                # Look for form elements with same ID pattern
                if element_id:
                    base_id = element_id.replace("slider", "").replace("range", "")
                    related_inputs = self.driver.find_elements(By.CSS_SELECTOR,
                                                               f"input[id$='{base_id}'], input[id^='{base_id}']")
                    if related_inputs:
                        alternatives.append({
                            "type": "related_input",
                            "element_tag": related_inputs[0].tag_name,
                            "element_id": related_inputs[0].get_attribute("id") or ""
                        })

                # Check for increment/decrement buttons
                parent = draggable_element.find_element(By.XPATH, "./..")
                buttons = parent.find_elements(By.CSS_SELECTOR, "button, [role='button']")
                if buttons:
                    alternatives.append({
                        "type": "buttons",
                        "count": len(buttons)
                    })

                # Check for keyboard accessibility
                try:
                    draggable_element.send_keys(Keys.ARROW_RIGHT)
                    new_value1 = draggable_element.get_attribute("value")
                    draggable_element.send_keys(Keys.ARROW_LEFT)
                    new_value2 = draggable_element.get_attribute("value")

                    if new_value1 != new_value2:
                        alternatives.append({
                            "type": "keyboard_accessible"
                        })
                except Exception:
                    pass

            # 2. Check for sortable/draggable alternatives (up/down buttons, numeric inputs)
            elif element_tag in ["li", "div", "tr"] or "draggable" in draggable_element.get_attribute("class").lower():
                # Look for move buttons
                move_buttons = self.driver.find_elements(By.CSS_SELECTOR,
                                                         "button:contains('Move'), button[aria-label*='move'], button[title*='move'], " +
                                                         "button:contains('Up'), button:contains('Down'), button[aria-label*='up'], button[aria-label*='down']"
                                                         )

                if move_buttons:
                    alternatives.append({
                        "type": "move_buttons",
                        "count": len(move_buttons)
                    })

                # Look for order inputs
                parent = self.driver.find_element(By.XPATH, "./ancestor::*[position()=3]")
                order_inputs = parent.find_elements(By.CSS_SELECTOR, "input[type='number'], select")

                if order_inputs:
                    alternatives.append({
                        "type": "order_inputs",
                        "count": len(order_inputs)
                    })

            # 3. Check for keyboard accessibility for all draggable elements
            try:
                # Set focus to the element
                self.driver.execute_script("arguments[0].focus();", draggable_element)

                # Look for ARIA attributes that indicate keyboard support
                aria_keyshortcuts = draggable_element.get_attribute("aria-keyshortcuts")

                if aria_keyshortcuts:
                    alternatives.append({
                        "type": "aria_keyshortcuts",
                        "shortcuts": aria_keyshortcuts
                    })
            except Exception:
                pass

            # 4. Check for general touch alternatives
            touch_alternatives = self.driver.execute_script("""
                var el = arguments[0];

                // Check for tap handlers
                var hasTapHandler = (
                    el.onclick || 
                    el.addEventListener && el._events && (el._events.click || el._events.tap)
                );

                // Check for touch handlers
                var hasTouchHandler = (
                    el.ontouchstart || el.ontouchend ||
                    el.addEventListener && el._events && (el._events.touchstart || el._events.touchend)
                );

                return {
                    has_click_handler: !!hasTapHandler,
                    has_touch_handler: !!hasTouchHandler
                };
            """, draggable_element)

            if touch_alternatives.get("has_click_handler") or touch_alternatives.get("has_touch_handler"):
                alternatives.append({
                    "type": "touch_handlers",
                    "details": touch_alternatives
                })

            return len(alternatives) > 0, alternatives

        except Exception as e:
            self.logger.error(f"Error finding dragging alternatives: {str(e)}")
            return False, {"error": str(e)}

    def test_consistent_help_across_pages(self, urls, test_dir=None):
        """
        Test for WCAG 2.2 Success Criterion 3.2.6: Consistent Help across multiple pages.

        This test needs to be run across multiple pages to verify help mechanisms
        appear in the same relative order on each page.

        Args:
            urls (list): List of URLs to test
            test_dir (str, optional): Directory to save test results

        Returns:
            dict: Test results for consistent help across pages
        """
        self.logger.info("Testing 3.2.6: Consistent Help across pages")

        criterion_results = {
            "criterion": "3.2.6",
            "name": "Consistent Help",
            "level": "A",
            "description": "If help mechanisms are provided, they occur in the same relative order across pages.",
            "issues": [],
            "passed": True,
            "pages_tested": len(urls),
            "help_mechanisms_by_page": {}
        }

        try:
            # First collect help mechanisms from all pages
            for url in urls:
                self.logger.info(f"Checking help mechanisms on {url}")

                # Navigate to the page
                self.driver.get(url)
                time.sleep(3)  # Allow page to load

                # Find help mechanisms on this page
                help_mechanisms = self._find_help_mechanisms_detailed()

                # Store for this page
                criterion_results["help_mechanisms_by_page"][url] = help_mechanisms

            # If we have multiple pages to compare
            if len(urls) > 1:
                # Get the first page as reference
                first_url = urls[0]
                reference_mechanisms = criterion_results["help_mechanisms_by_page"][first_url]

                # Get categories of help found on the first page
                reference_categories = {}

                for mechanism in reference_mechanisms:
                    category = mechanism["category"]
                    if category not in reference_categories:
                        reference_categories[category] = []
                    reference_categories[category].append(mechanism)

                # Compare with other pages
                for url in urls[1:]:
                    current_mechanisms = criterion_results["help_mechanisms_by_page"][url]

                    # Check if mechanisms are missing
                    for category, ref_mechanisms in reference_categories.items():
                        # See if this category exists on the current page
                        current_category_mechanisms = [m for m in current_mechanisms if m["category"] == category]

                        if not current_category_mechanisms and ref_mechanisms:
                            criterion_results["issues"].append({
                                "issue_type": "missing_category",
                                "message": f"Help category '{category}' found on {first_url} is missing on {url}",
                                "reference_page": first_url,
                                "current_page": url
                            })
                            criterion_results["passed"] = False
                            continue

                        # Check for differences in ordering
                        if len(ref_mechanisms) > 0 and len(current_category_mechanisms) > 0:
                            ref_types = [m["type"] for m in ref_mechanisms]
                            current_types = [m["type"] for m in current_category_mechanisms]

                            # Check if sequences match (allowing for missing items)
                            is_sequence_consistent = True

                            # Compare ordering of types that exist on both pages
                            common_types = list(set(ref_types) & set(current_types))

                            if len(common_types) > 1:  # Only check if we have at least two common types
                                ref_order = [ref_types.index(t) for t in common_types]
                                current_order = [current_types.index(t) for t in common_types]

                                # Check if relative ordering is maintained
                                for i in range(len(common_types) - 1):
                                    for j in range(i + 1, len(common_types)):
                                        if (ref_order[i] < ref_order[j] and current_order[i] > current_order[j]) or \
                                                (ref_order[i] > ref_order[j] and current_order[i] < current_order[j]):
                                            is_sequence_consistent = False
                                            break

                            if not is_sequence_consistent:
                                criterion_results["issues"].append({
                                    "issue_type": "inconsistent_order",
                                    "message": f"Help mechanisms in category '{category}' appear in different order on {url} compared to {first_url}",
                                    "reference_page": first_url,
                                    "current_page": url,
                                    "reference_order": ref_types,
                                    "current_order": current_types
                                })
                                criterion_results["passed"] = False

            # Generate summary
            if criterion_results["passed"]:
                criterion_results["summary"] = "Help mechanisms are consistent across all tested pages"
            else:
                criterion_results[
                    "summary"] = f"Found {len(criterion_results['issues'])} inconsistencies in help mechanisms across pages"

        except Exception as e:
            self.logger.error(f"Error in consistent help test: {str(e)}")
            criterion_results["error"] = str(e)

        return criterion_results

    def _find_help_mechanisms_detailed(self):
        """
        Find detailed help mechanisms on the current page.

        Returns:
            list: List of help mechanisms with detailed information
        """
        help_mechanisms = []

        try:
            # Use JavaScript to find and categorize help mechanisms
            results = self.driver.execute_script("""
                function getElementPath(element) {
                    // Create a path like "body > header > nav > div.menu > a.help"
                    var path = [];
                    while (element && element.tagName) {
                        let selector = element.tagName.toLowerCase();
                        if (element.id) {
                            selector += '#' + element.id;
                        } else if (element.className) {
                            selector += '.' + element.className.replace(/\\s+/g, '.');
                        }
                        path.unshift(selector);
                        element = element.parentElement;
                    }
                    return path.join(' > ');
                }

                function getRelativePosition(element) {
                    // Get position information relative to document
                    var docRect = document.documentElement.getBoundingClientRect();
                    var elemRect = element.getBoundingClientRect();

                    return {
                        top: elemRect.top - docRect.top,
                        left: elemRect.left - docRect.left,
                        bottom: elemRect.bottom - docRect.top,
                        right: elemRect.right - docRect.left,
                        width: elemRect.width,
                        height: elemRect.height
                    };
                }

                function getCategoryAndType(element) {
                    // Determine the category and type of help mechanism
                    var href = element.href || "";
                    var text = element.textContent.trim().toLowerCase();
                    var classes = (element.className || "").toLowerCase();
                    var id = (element.id || "").toLowerCase();
                    var ariaLabel = (element.getAttribute("aria-label") || "").toLowerCase();

                    var category = "unknown";
                    var type = "unknown";

                    // Human contact details
                    if (href.startsWith("mailto:")) {
                        category = "human_contact";
                        type = "email";
                    } else if (href.startsWith("tel:")) {
                        category = "human_contact";
                        type = "phone";
                    } else if (text.includes("contact") || id.includes("contact") || 
                               classes.includes("contact") || ariaLabel.includes("contact")) {
                        category = "human_contact";
                        type = "contact_page";
                    }

                    // Live human help
                    else if (text.includes("chat") || id.includes("chat") || 
                             classes.includes("chat") || ariaLabel.includes("chat")) {
                        category = "human_contact";
                        type = "live_chat";
                    } else if (text.includes("support") || id.includes("support") || 
                               classes.includes("support") || ariaLabel.includes("support")) {
                        category = "human_contact";
                        type = "support";
                    }

                    // Self-help options
                    else if (text.includes("help") || id.includes("help") || 
                             classes.includes("help") || ariaLabel.includes("help")) {
                        category = "self_help";
                        type = "help_page";
                    } else if (text.includes("faq") || id.includes("faq") || 
                               classes.includes("faq") || ariaLabel.includes("faq") ||
                               text.includes("frequently asked")) {
                        category = "self_help";
                        type = "faq";
                    } else if (text.includes("guide") || id.includes("guide") || 
                               classes.includes("guide") || ariaLabel.includes("guide")) {
                        category = "self_help";
                        type = "guide";
                    }

                    // Automated contact mechanism
                    else if (text.includes("chatbot") || id.includes("chatbot") || 
                             classes.includes("chatbot") || ariaLabel.includes("chatbot") ||
                             text.includes("virtual assistant") || id.includes("virtual-assistant")) {
                        category = "automated_contact";
                        type = "chatbot";
                    } else if (text.includes("feedback") || id.includes("feedback") || 
                               classes.includes("feedback") || ariaLabel.includes("feedback")) {
                        category = "automated_contact";
                        type = "feedback_form";
                    }

                    return { category, type };
                }

                // Find all potential help mechanisms
                var helpSelectors = [
                    "a[href^='mailto:']",
                    "a[href^='tel:']",
                    "a[href*='contact']",
                    "a[href*='help']",
                    "a[href*='support']",
                    "a[href*='faq']",
                    "a[href*='chat']",
                    "button:contains('chat')",
                    "button:contains('help')",
                    "button:contains('contact')",
                    "button:contains('support')",
                    "[role='button']:contains('chat')",
                    "[role='button']:contains('help')",
                    "[role='button']:contains('contact')",
                    "[role='button']:contains('support')",
                    "[class*='chat']",
                    "[class*='help']",
                    "[class*='contact']",
                    "[class*='support']",
                    "[class*='faq']",
                    "[id*='chat']",
                    "[id*='help']",
                    "[id*='contact']",
                    "[id*='support']",
                    "[id*='faq']",
                    "[aria-label*='chat']",
                    "[aria-label*='help']",
                    "[aria-label*='contact']",
                    "[aria-label*='support']"
                ];

                // Custom contains selector 
                function findWithText(selector, text) {
                    var elements = document.querySelectorAll(selector);
                    return Array.from(elements).filter(el => 
                        el.textContent.toLowerCase().includes(text.toLowerCase())
                    );
                }

                var helpElements = [];

                // Find elements matching our selectors
                helpSelectors.forEach(selector => {
                    if (selector.includes(":contains(")) {
                        // Handle custom contains selector
                        const parts = selector.match(/(.+):contains\('(.+)'\)/);
                        if (parts && parts.length === 3) {
                            const baseSelector = parts[1];
                            const text = parts[2];
                            const found = findWithText(baseSelector, text);
                            helpElements = helpElements.concat(found);
                        }
                    } else {
                        try {
                            const found = document.querySelectorAll(selector);
                            helpElements = helpElements.concat(Array.from(found));
                        } catch (e) {
                            // Skip invalid selectors
                            console.error("Invalid selector:", selector);
                        }
                    }
                });

                // Remove duplicates
                helpElements = Array.from(new Set(helpElements));

                // Process each help mechanism
                var results = helpElements.map(element => {
                    var categoryAndType = getCategoryAndType(element);

                    return {
                        element: element.tagName.toLowerCase(),
                        text: element.textContent.trim(),
                        href: element.href || null,
                        path: getElementPath(element),
                        position: getRelativePosition(element),
                        category: categoryAndType.category,
                        type: categoryAndType.type,
                        aria_label: element.getAttribute("aria-label") || null,
                        id: element.id || null,
                        class_name: element.className || null
                    };
                });

                return results;
            """)

            # Process the JavaScript results
            if results:
                help_mechanisms = results

                # Add screenshot path for evidence
                screenshot_path = os.path.join(self.output_dir, "help_mechanisms.png")
                self.driver.save_screenshot(screenshot_path)

            return help_mechanisms

        except Exception as e:
            self.logger.error(f"Error finding help mechanisms: {str(e)}")
            return []

    def _test_3_3_9_redundant_entry_enhanced(self):
        """
        Enhanced test for WCAG 2.2 Success Criterion 3.3.9: Redundant Entry.

        Information previously entered by or provided to the user that is required to be
        entered again is auto-populated, or available for the user to select.

        This enhanced version tests more form scenarios and actively fills forms.
        """
        self.logger.info("Testing 3.3.9: Redundant Entry (Enhanced)")

        criterion_results = {
            "criterion": "3.3.9",
            "name": "Redundant Entry",
            "level": "A",
            "description": "Information previously entered by or provided to the user is auto-populated, or available for selection.",
            "issues": [],
            "passed": True
        }

        try:
            # Find multi-step forms
            multi_step_forms = self._find_multi_step_forms()

            if multi_step_forms:
                self.logger.info(f"Found {len(multi_step_forms)} potential multi-step forms")

                for form_info in multi_step_forms:
                    # Test each multi-step form for redundant entry
                    self._test_multi_step_form_for_redundancy(form_info, criterion_results)

            # Find other forms with potential redundant entry
            normal_forms = self._find_regular_forms()

            if normal_forms:
                self.logger.info(f"Found {len(normal_forms)} regular forms")

                for form_info in normal_forms:
                    # Test each form for redundancy patterns
                    self._test_form_for_redundancy_patterns(form_info, criterion_results)

            # Check for autocomplete attributes on form fields
            self._check_autocomplete_attributes(criterion_results)

            # Test user-provided information in non-form contexts
            self._test_non_form_redundant_info(criterion_results)

            # If no forms found, mark as not applicable
            if not multi_step_forms and not normal_forms:
                criterion_results["not_applicable"] = True
                criterion_results["summary"] = "No forms requiring user information found on page"
                return criterion_results

        except Exception as e:
            self.logger.error(f"Error in redundant entry test: {str(e)}")
            criterion_results["error"] = str(e)

        if criterion_results["passed"]:
            criterion_results["summary"] = "No redundant entry issues found"
        else:
            criterion_results["summary"] = f"Found {len(criterion_results['issues'])} potential redundant entry issues"

        return criterion_results

    def _find_multi_step_forms(self):
        """Find multi-step forms on the page."""
        multi_step_forms = self.driver.execute_script("""
            function findMultiStepForms() {
                var results = [];

                // Indicators of multi-step forms
                var multiStepIndicators = [
                    // Wizard/stepper classes and IDs
                    "[class*='wizard']", "[id*='wizard']", 
                    "[class*='stepper']", "[id*='stepper']",
                    "[class*='multi-step']", "[id*='multi-step']",
                    "[class*='steps']", "[id*='steps']",
                    // Progress indicators
                    ".progress", "#progress",
                    // Step navigation
                    "[class*='next']", "[class*='prev']",
                    "button:contains('Next')", "button:contains('Previous')",
                    "button:contains('Continue')", "button:contains('Back')",
                    // Form with multiple fieldsets
                    "form fieldset", "form .step", "form [class*='step']"
                ];

                // Function to find text in elements
                function findWithText(selector, text) {
                    try {
                        var elements = document.querySelectorAll(selector);
                        return Array.from(elements).filter(el => 
                            el.textContent.toLowerCase().includes(text.toLowerCase())
                        );
                    } catch (e) {
                        return [];
                    }
                }

                // Find potential multi-step containers
                var potentialContainers = [];

                multiStepIndicators.forEach(selector => {
                    try {
                        if (selector.includes(":contains(")) {
                            // Handle text contains selector
                            const match = selector.match(/(.+):contains\('(.+)'\)/);
                            if (match && match.length === 3) {
                                const baseSelector = match[1];
                                const text = match[2];
                                const found = findWithText(baseSelector, text);
                                potentialContainers = potentialContainers.concat(found);
                            }
                        } else {
                            // Standard selector
                            const found = document.querySelectorAll(selector);
                            potentialContainers = potentialContainers.concat(Array.from(found));
                        }
                    } catch(e) {
                        // Skip invalid selectors
                    }
                });

                // Remove duplicates
                potentialContainers = Array.from(new Set(potentialContainers));

                // Find the forms these indicators belong to
                potentialContainers.forEach(container => {
                    // Find parent form
                    let form = container.closest('form');

                    // If no parent form, container might be the form itself
                    if (!form && container.tagName === 'FORM') {
                        form = container;
                    }

                    // If still no form, this might be a JS-based form without <form> tag
                    // Use container as the "form"
                    if (!form) {
                        form = container;
                    }

                    if (form) {
                        // Get form information
                        const formInfo = {
                            element: form,
                            id: form.id || null,
                            className: form.className || null,
                            action: form.getAttribute('action') || null,
                            indicator: container.tagName + (container.id ? '#' + container.id : '') + 
                                      (container.className ? '.' + container.className.replace(/\\s+/g, '.') : ''),
                            inputs: Array.from(form.querySelectorAll('input, select, textarea')).map(input => ({
                                name: input.name || null,
                                id: input.id || null,
                                type: input.type || null,
                                autocomplete: input.getAttribute('autocomplete') || null
                            }))
                        };

                        // Only include if it wasn't already found
                        if (!results.some(r => r.id === formInfo.id && r.action === formInfo.action)) {
                            results.push(formInfo);
                        }
                    }
                });

                // Additionally, look for forms with step navigation buttons
                document.querySelectorAll('form').forEach(form => {
                    // Look for next/prev buttons
                    const nextButtons = form.querySelectorAll('[class*="next"], [id*="next"], [class*="continue"]');
                    const prevButtons = form.querySelectorAll('[class*="prev"], [id*="prev"], [class*="back"]');

                    if (nextButtons.length > 0 || prevButtons.length > 0) {
                        // This form likely has multiple steps
                        const formInfo = {
                            element: form,
                            id: form.id || null,
                            className: form.className || null,
                            action: form.getAttribute('action') || null,
                            indicator: 'Has navigation buttons',
                            inputs: Array.from(form.querySelectorAll('input, select, textarea')).map(input => ({
                                name: input.name || null,
                                id: input.id || null,
                                type: input.type || null,
                                autocomplete: input.getAttribute('autocomplete') || null
                            }))
                        };

                        // Only include if it wasn't already found
                        if (!results.some(r => r.id === formInfo.id && r.action === formInfo.action)) {
                            results.push(formInfo);
                        }
                    }
                });

                return results;
            }

            return findMultiStepForms();
        """)

        return multi_step_forms

    def _find_regular_forms(self):
        """Find regular forms with potential redundant entry patterns."""
        regular_forms = self.driver.execute_script("""
            function findRegularForms() {
                var results = [];

                // Get all forms on the page
                var forms = document.querySelectorAll('form');

                forms.forEach(form => {
                    // Get all inputs
                    var inputs = form.querySelectorAll('input, select, textarea');

                    // Only include forms with inputs
                    if (inputs.length > 0) {
                        const formInfo = {
                            element: form,
                            id: form.id || null,
                            className: form.className || null,
                            action: form.getAttribute('action') || null,
                            inputs: Array.from(inputs).map(input => ({
                                name: input.name || null,
                                id: input.id || null,
                                type: input.type || null,
                                autocomplete: input.getAttribute('autocomplete') || null,
                                placeholder: input.getAttribute('placeholder') || null,
                                label: input.labels && input.labels.length > 0 ? input.labels[0].textContent.trim() : null
                            }))
                        };

                        results.push(formInfo);
                    }
                });

                return results;
            }

            return findRegularForms();
        """)

        return regular_forms

    def _test_multi_step_form_for_redundancy(self, form_info, criterion_results):
        """Test a multi-step form for redundant entry issues."""
        try:
            # Try to identify steps and navigation
            form_element = form_info["element"]

            # Look for "Next" buttons to navigate between steps
            next_buttons = self.driver.execute_script("""
                var form = arguments[0];

                // Find next buttons
                var nextSelectors = [
                    "button:contains('Next')", "button:contains('Continue')",
                    "input[type='submit'][value*='Next']", "input[type='button'][value*='Next']",
                    "[class*='next']", "[id*='next']", "[class*='continue']",
                    "[role='button']:contains('Next')"
                ];

                function findWithText(selector, text) {
                    try {
                        var elements = document.querySelectorAll(selector);
                        return Array.from(elements).filter(el => 
                            el.textContent.toLowerCase().includes(text.toLowerCase())
                        );
                    } catch (e) {
                        return [];
                    }
                }

                var buttons = [];

                nextSelectors.forEach(selector => {
                    try {
                        if (selector.includes(":contains(")) {
                            // Handle text contains selector
                            const match = selector.match(/(.+):contains\('(.+)'\)/);
                            if (match && match.length === 3) {
                                const baseSelector = match[1];
                                const text = match[2];
                                const found = findWithText(baseSelector, text);
                                buttons = buttons.concat(found);
                            }
                        } else {
                            // Standard selector - look inside the form
                            const found = form.querySelectorAll(selector);
                            buttons = buttons.concat(Array.from(found));
                        }
                    } catch(e) {
                        // Skip invalid selectors
                    }
                });

                // Remove duplicates
                return Array.from(new Set(buttons));
            """, form_element)

            # If there are no navigation buttons, we can't test the form steps
            if not next_buttons:
                self.logger.info("No navigation buttons found in multi-step form")
                return

            # Save the initial form state to check for redundant fields
            initial_fields = self.driver.execute_script("""
                var form = arguments[0];

                // Get all visible input fields
                return Array.from(form.querySelectorAll('input:not([type="hidden"]), select, textarea'))
                    .filter(el => {
                        var style = window.getComputedStyle(el);
                        return style.display !== 'none' && style.visibility !== 'hidden';
                    })
                    .map(field => ({
                        name: field.name || null,
                        id: field.id || null,
                        type: field.type || null,
                        value: field.value || null
                    }));
            """, form_element)

            # Fill out the first step with test data
            self._fill_form_fields(form_element)

            # Click the first "Next" button to navigate to the next step
            if next_buttons:
                next_button = next_buttons[0]
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(1)  # Wait for next step to load

                # Check if new form step has loaded
                new_fields = self.driver.execute_script("""
                    var form = arguments[0];

                    // Get all visible input fields
                    return Array.from(form.querySelectorAll('input:not([type="hidden"]), select, textarea'))
                        .filter(el => {
                            var style = window.getComputedStyle(el);
                            return style.display !== 'none' && style.visibility !== 'hidden';
                        })
                        .map(field => ({
                            name: field.name || null,
                            id: field.id || null,
                            type: field.type || null,
                            value: field.value || null
                        }));
                """, form_element)

                # Look for fields requesting information that was already provided
                redundant_fields = []
                for new_field in new_fields:
                    for initial_field in initial_fields:
                        # Check for fields with same name or similar ID but empty value
                        if (new_field["name"] and new_field["name"] == initial_field["name"]) or \
                                (new_field["id"] and initial_field["id"] and
                                 (new_field["id"] == initial_field["id"] or
                                  new_field["id"].startswith(initial_field["id"]) or
                                  initial_field["id"].startswith(new_field["id"]))):

                            # If the field doesn't have a value but the original did
                            if not new_field["value"] and initial_field["value"]:
                                redundant_fields.append({
                                    "original_field": initial_field,
                                    "redundant_field": new_field
                                })

                # Report any redundant fields found
                if redundant_fields:
                    for redundant in redundant_fields:
                        criterion_results["issues"].append({
                            "element": "form",
                            "element_info": {
                                "id": form_info["id"],
                                "class": form_info["className"],
                                "action": form_info["action"]
                            },
                            "issue_type": "multi_step_redundant_entry",
                            "message": f"Multi-step form requests the same information more than once",
                            "details": {
                                "original_field": redundant["original_field"],
                                "redundant_field": redundant["redundant_field"]
                            }
                        })
                        criterion_results["passed"] = False

        except Exception as e:
            self.logger.error(f"Error testing multi-step form for redundancy: {str(e)}")

    def _test_form_for_redundancy_patterns(self, form_info, criterion_results):
        """Test a form for common redundancy patterns."""
        try:
            inputs = form_info.get("inputs", [])

            # Check for verification fields (common redundant entry pattern)
            verification_fields = []
            for i, field1 in enumerate(inputs):
                for field2 in inputs[i + 1:]:
                    # Fields with similar names or ids
                    name_similarity = False
                    id_similarity = False

                    if field1["name"] and field2["name"]:
                        name1 = field1["name"].lower()
                        name2 = field2["name"].lower()

                        # Check for common verification patterns
                        name_similarity = (
                                (name1 == name2 + "confirm" or name2 == name1 + "confirm") or
                                (name1 == name2 + "verify" or name2 == name1 + "verify") or
                                (name1 == "confirm" + name2 or name2 == "confirm" + name1) or
                                (name1 == "verify" + name2 or name2 == "verify" + name1) or
                                (name1 == name2 + "2" or name2 == name1 + "2") or
                                (name1 + "2" == name2 or name2 + "2" == name1)
                        )

                    if field1["id"] and field2["id"]:
                        id1 = field1["id"].lower()
                        id2 = field2["id"].lower()

                        # Check for common verification patterns
                        id_similarity = (
                                (id1 == id2 + "confirm" or id2 == id1 + "confirm") or
                                (id1 == id2 + "verify" or id2 == id1 + "verify") or
                                (id1 == "confirm" + id2 or id2 == "confirm" + id1) or
                                (id1 == "verify" + id2 or id2 == "verify" + id1) or
                                (id1 == id2 + "2" or id2 == id1 + "2") or
                                (id1 + "2" == id2 or id2 + "2" == id1)
                        )

                    # Fields with similar types
                    type_match = field1["type"] == field2["type"]

                    # Check if both fields are common types that often have confirmation
                    common_verification_type = field1["type"] in ["email", "password", "text"] and type_match

                    if (name_similarity or id_similarity) and common_verification_type:
                        verification_fields.append({
                            "field1": field1,
                            "field2": field2
                        })

            # For each potential verification field pair, check autocomplete
            for pair in verification_fields:
                field1 = pair["field1"]
                field2 = pair["field2"]

                # Email confirmation should use autocomplete
                if field1["type"] == "email" and field2["type"] == "email":
                    # Second field should have autocomplete or be prefilled
                    if field2["autocomplete"] == "off" or not field2["autocomplete"]:
                        criterion_results["issues"].append({
                            "element": "input",
                            "element_info": {
                                "id": field2["id"],
                                "name": field2["name"],
                                "type": field2["type"]
                            },
                            "issue_type": "confirmation_field_without_autocomplete",
                            "message": f"Email confirmation field does not support autocomplete",
                            "details": {
                                "primary_field": field1,
                                "confirmation_field": field2
                            }
                        })
                        criterion_results["passed"] = False

        except Exception as e:
            self.logger.error(f"Error testing form for redundancy patterns: {str(e)}")

    def _check_autocomplete_attributes(self, criterion_results):
        """Check if form fields have appropriate autocomplete attributes."""
        try:
            autocomplete_issues = self.driver.execute_script("""
                // Fields that should typically have autocomplete
                var commonFields = [
                    { name: "name", autocomplete: ["name", "given-name", "family-name"] },
                    { name: "email", autocomplete: ["email"] },
                    { name: "address", autocomplete: ["address-line1", "address-line2", "street-address"] },
                    { name: "city", autocomplete: ["address-level2"] },
                    { name: "state", autocomplete: ["address-level1"] },
                    { name: "zip", autocomplete: ["postal-code"] },
                    { name: "country", autocomplete: ["country", "country-name"] },
                    { name: "phone", autocomplete: ["tel", "tel-national"] },
                    { name: "cardnumber", autocomplete: ["cc-number"] },
                    { name: "cc-exp", autocomplete: ["cc-exp", "cc-exp-month", "cc-exp-year"] },
                    { name: "ccv", autocomplete: ["cc-csc"] }
                ];

                var issues = [];

                // Get all input fields
                var fields = document.querySelectorAll('input:not([type="hidden"]), select, textarea');

                // Check each field
                fields.forEach(field => {
                    var fieldName = field.name ? field.name.toLowerCase() : '';
                    var fieldId = field.id ? field.id.toLowerCase() : '';
                    var fieldType = field.type || '';
                    var autocomplete = field.getAttribute('autocomplete');

                    // Skip submit buttons, checkboxes, etc.
                    if (fieldType === 'submit' || fieldType === 'button' || 
                        fieldType === 'checkbox' || fieldType === 'radio') {
                        return;
                    }

                    // Check for specific field types
                    for (var commonField of commonFields) {
                        // See if field name or ID contains the common field name
                        if (fieldName.includes(commonField.name) || fieldId.includes(commonField.name)) {
                            // It should have an appropriate autocomplete attribute
                            if (!autocomplete || autocomplete === 'off') {
                                issues.push({
                                    id: fieldId,
                                    name: fieldName,
                                    type: fieldType,
                                    expected_autocomplete: commonField.autocomplete.join(' or '),
                                    current_autocomplete: autocomplete || 'none'
                                });
                            } else {
                                // Check if autocomplete value is one of the expected ones
                                var validAutocomplete = commonField.autocomplete.some(ac => 
                                    autocomplete.includes(ac)
                                );

                                if (!validAutocomplete) {
                                    issues.push({
                                        id: fieldId,
                                        name: fieldName,
                                        type: fieldType,
                                        expected_autocomplete: commonField.autocomplete.join(' or '),
                                        current_autocomplete: autocomplete
                                    });
                                }
                            }
                        }
                    }
                });

                return issues;
            """)

            # Add issues to results
            for issue in autocomplete_issues:
                criterion_results["issues"].append({
                    "element": "input",
                    "element_info": {
                        "id": issue["id"],
                        "name": issue["name"],
                        "type": issue["type"]
                    },
                    "issue_type": "missing_appropriate_autocomplete",
                    "message": f"Field should have autocomplete attribute to reduce redundant entry",
                    "details": {
                        "expected": issue["expected_autocomplete"],
                        "current": issue["current_autocomplete"]
                    }
                })
                criterion_results["passed"] = False

        except Exception as e:
            self.logger.error(f"Error checking autocomplete attributes: {str(e)}")

    def _test_non_form_redundant_info(self, criterion_results):
        """Test for redundant information entry in non-form contexts."""
        try:
            # Check for common UI patterns that might require redundant entry
            # For example, account creation flows, checkout processes, etc.
            redundant_ui_patterns = self.driver.execute_script("""
                // Look for account creation sections
                var accountCreationIndicators = [
                    "h1:contains('Create Account')", "h2:contains('Create Account')",
                    "h1:contains('Sign Up')", "h2:contains('Sign Up')",
                    "h1:contains('Register')", "h2:contains('Register')"
                ];

                // Look for checkout processes
                var checkoutIndicators = [
                    "h1:contains('Checkout')", "h2:contains('Checkout')",
                    "h1:contains('Payment')", "h2:contains('Payment')",
                    "h1:contains('Shipping')", "h2:contains('Shipping')"
                ];

                function findWithText(selector, text) {
                    try {
                        var base = selector.split(':contains(')[0];
                        var elements = document.querySelectorAll(base);
                        return Array.from(elements).filter(el => 
                            el.textContent.toLowerCase().includes(text.toLowerCase())
                        );
                    } catch (e) {
                        return [];
                    }
                }

                var foundIndicators = [];

                // Check account creation indicators
                accountCreationIndicators.forEach(indicator => {
                    if (indicator.includes(':contains(')) {
                        const match = indicator.match(/(.+):contains\('(.+)'\)/);
                        if (match && match.length === 3) {
                            const elements = findWithText(match[1], match[2]);
                            if (elements.length > 0) {
                                foundIndicators.push({
                                    type: 'account_creation',
                                    element: elements[0].tagName,
                                    text: elements[0].textContent.trim()
                                });
                            }
                        }
                    }
                });

                // Check checkout indicators
                checkoutIndicators.forEach(indicator => {
                    if (indicator.includes(':contains(')) {
                        const match = indicator.match(/(.+):contains\('(.+)'\)/);
                        if (match && match.length === 3) {
                            const elements = findWithText(match[1], match[2]);
                            if (elements.length > 0) {
                                foundIndicators.push({
                                    type: 'checkout',
                                    element: elements[0].tagName,
                                    text: elements[0].textContent.trim()
                                });
                            }
                        }
                    }
                });

                return foundIndicators;
            """)

            # If we found relevant UI patterns, check for specific features
            if redundant_ui_patterns:
                for pattern in redundant_ui_patterns:
                    if pattern["type"] == "account_creation":
                        # For account creation, check if there's a social login option
                        # (which reduces redundant entry)
                        social_login = self.driver.execute_script("""
                            // Look for social login buttons
                            var socialLoginIndicators = [
                                "a[href*='facebook'], button[class*='facebook']",
                                "a[href*='google'], button[class*='google']",
                                "a[href*='twitter'], button[class*='twitter']",
                                "a[href*='apple'], button[class*='apple']",
                                "[class*='social-login']", "[id*='social-login']",
                                "[class*='oauth']", "[id*='oauth']",
                                "[class*='sso']", "[id*='sso']"
                            ];

                            var found = [];

                            socialLoginIndicators.forEach(selector => {
                                try {
                                    const elements = document.querySelectorAll(selector);
                                    if (elements.length > 0) {
                                        found.push({
                                            selector: selector,
                                            count: elements.length
                                        });
                                    }
                                } catch (e) {}
                            });

                            return found;
                        """)

                        if not social_login:
                            criterion_results["issues"].append({
                                "element": pattern["element"],
                                "element_info": {
                                    "text": pattern["text"],
                                    "type": pattern["type"]
                                },
                                "issue_type": "account_creation_without_alternatives",
                                "message": "Account creation process lacks social login options to reduce redundant entry",
                                "details": {
                                    "recommendation": "Add social login options or other account creation alternatives"
                                }
                            })
                            criterion_results["passed"] = False

                    elif pattern["type"] == "checkout":
                        # For checkout, check if there's a guest checkout option
                        # (which reduces redundant account creation)
                        guest_checkout = self.driver.execute_script("""
                            // Look for guest checkout options
                            var guestCheckoutIndicators = [
                                "a:contains('Guest Checkout')", "button:contains('Guest Checkout')",
                                "a:contains('Continue as Guest')", "button:contains('Continue as Guest')",
                                "input[value*='guest']", "a[href*='guest']",
                                "[class*='guest-checkout']", "[id*='guest-checkout']"
                            ];

                            function findWithText(selector, text) {
                                try {
                                    var base = selector.split(':contains(')[0];
                                    var elements = document.querySelectorAll(base);
                                    return Array.from(elements).filter(el => 
                                        el.textContent.toLowerCase().includes(text.toLowerCase())
                                    );
                                } catch (e) {
                                    return [];
                                }
                            }

                            var found = [];

                            guestCheckoutIndicators.forEach(indicator => {
                                try {
                                    if (indicator.includes(':contains(')) {
                                        const match = indicator.match(/(.+):contains\('(.+)'\)/);
                                        if (match && match.length === 3) {
                                            const elements = findWithText(match[1], match[2]);
                                            if (elements.length > 0) {
                                                found.push({
                                                    indicator: indicator,
                                                    count: elements.length
                                                });
                                            }
                                        }
                                    } else {
                                        const elements = document.querySelectorAll(indicator);
                                        if (elements.length > 0) {
                                            found.push({
                                                indicator: indicator,
                                                count: elements.length
                                            });
                                        }
                                    }
                                } catch (e) {}
                            });

                            return found;
                        """)

                        if not guest_checkout:
                            # Also check for saved addresses/payment methods
                            saved_info = self.driver.execute_script("""
                                // Look for saved info options
                                var savedInfoIndicators = [
                                    "a:contains('Saved Addresses')", "button:contains('Saved Addresses')",
                                    "a:contains('Saved Payment')", "button:contains('Saved Payment')",
                                    "[class*='saved-address']", "[id*='saved-address']",
                                    "[class*='saved-payment']", "[id*='saved-payment']",
                                    "[class*='saved-card']", "[id*='saved-card']"
                                ];

                                function findWithText(selector, text) {
                                    try {
                                        var base = selector.split(':contains(')[0];
                                        var elements = document.querySelectorAll(base);
                                        return Array.from(elements).filter(el => 
                                            el.textContent.toLowerCase().includes(text.toLowerCase())
                                        );
                                    } catch (e) {
                                        return [];
                                    }
                                }

                                var found = [];

                                savedInfoIndicators.forEach(indicator => {
                                    try {
                                        if (indicator.includes(':contains(')) {
                                            const match = indicator.match(/(.+):contains\('(.+)'\)/);
                                            if (match && match.length === 3) {
                                                const elements = findWithText(match[1], match[2]);
                                                if (elements.length > 0) {
                                                    found.push({
                                                        indicator: indicator,
                                                        count: elements.length
                                                    });
                                                }
                                            }
                                        } else {
                                            const elements = document.querySelectorAll(indicator);
                                            if (elements.length > 0) {
                                                found.push({
                                                    indicator: indicator,
                                                    count: elements.length
                                                });
                                            }
                                        }
                                    } catch (e) {}
                                });

                                return found;
                            """)

                            if not saved_info:
                                criterion_results["issues"].append({
                                    "element": pattern["element"],
                                    "element_info": {
                                        "text": pattern["text"],
                                        "type": pattern["type"]
                                    },
                                    "issue_type": "checkout_without_alternatives",
                                    "message": "Checkout process lacks options to avoid redundant entry (guest checkout, saved addresses)",
                                    "details": {
                                        "recommendation": "Add guest checkout option or saved information features"
                                    }
                                })
                                criterion_results["passed"] = False

        except Exception as e:
            self.logger.error(f"Error testing non-form redundant info: {str(e)}")

    def _fill_form_fields(self, form_element):
        """Fill form fields with test data."""
        try:
            # Find all input fields in the form
            form_fields = self.driver.execute_script("""
                var form = arguments[0];
                var fields = form.querySelectorAll('input:not([type="submit"]):not([type="button"]):not([type="hidden"]):not([type="checkbox"]):not([type="radio"]), textarea, select');

                return Array.from(fields).filter(field => {
                    var style = window.getComputedStyle(field);
                    return style.display !== 'none' && style.visibility !== 'hidden';
                });
            """, form_element)

            # Fill each field with appropriate test data
            for field in form_fields:
                field_type = field.get_attribute("type") or ""
                field_name = field.get_attribute("name") or ""
                field_id = field.get_attribute("id") or ""

                # Determine appropriate test data based on field type or name
                test_value = self._get_test_data_for_field(field_type, field_name, field_id)

                # Fill the field
                if field.tag_name.lower() == "select":
                    # For select dropdowns, choose an option
                    options = field.find_elements(By.TAG_NAME, "option")
                    if options and len(options) > 1:
                        # Choose the second option (index 1) to avoid default/placeholder
                        self.driver.execute_script("arguments[0].selectedIndex = 1;", field)
                else:
                    # For text inputs, set the value
                    self.driver.execute_script("arguments[0].value = arguments[1];", field, test_value)

        except Exception as e:
            self.logger.error(f"Error filling form fields: {str(e)}")

    def _get_test_data_for_field(self, field_type, field_name, field_id):
        """Get appropriate test data for a field based on type and name."""
        field_name_lower = field_name.lower()
        field_id_lower = field_id.lower()

        # Check for common field types
        if field_type == "email" or "email" in field_name_lower or "email" in field_id_lower:
            return "test@example.com"

        elif field_type == "password" or "password" in field_name_lower or "password" in field_id_lower:
            return "TestPassword123!"

        elif field_type == "tel" or "phone" in field_name_lower or "phone" in field_id_lower:
            return "5551234567"

        elif "name" in field_name_lower or "name" in field_id_lower:
            if "first" in field_name_lower or "first" in field_id_lower:
                return "John"
            elif "last" in field_name_lower or "last" in field_id_lower:
                return "Smith"
            else:
                return "John Smith"

        elif "address" in field_name_lower or "address" in field_id_lower:
            return "123 Main St"

        elif "city" in field_name_lower or "city" in field_id_lower:
            return "Springfield"

        elif "state" in field_name_lower or "state" in field_id_lower:
            return "IL"

        elif "zip" in field_name_lower or "postal" in field_name_lower or "zip" in field_id_lower or "postal" in field_id_lower:
            return "62701"

        elif "country" in field_name_lower or "country" in field_id_lower:
            return "United States"

        # Default for unknown fields
        return "Test Data"