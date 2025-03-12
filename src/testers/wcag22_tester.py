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
            results["results"]["2.4.11"] = self._test_2_4_11_focus_not_obscured()
            results["results"]["2.4.13"] = self._test_2_4_13_focus_appearance()
            results["results"]["2.5.7"] = self._test_2_5_7_dragging_movements()
            results["results"]["2.5.8"] = self._test_2_5_8_target_size()
            results["results"]["3.2.6"] = self._test_3_2_6_consistent_help()
            results["results"]["3.3.7"] = self._test_3_3_7_accessible_authentication()
            results["results"]["3.3.9"] = self._test_3_3_9_redundant_entry()

            # Add metadata
            results["summary"] = self._create_summary(results["results"])

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
        <title>WCAG 2.2 Accessibility Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            header {
                background-color: #f8f9fa;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 5px;
            }
            h1, h2, h3 {
                color: #205493;
            }
            .summary-box {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 30px;
            }
            .summary-item {
                flex: 1;
                min-width: 200px;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .passed { background-color: #e7f4e4; }
            .failed { background-color: #f9dede; }
            .warning { background-color: #fff1d2; }

            .criterion-card {
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-bottom: 30px;
                overflow: hidden;
            }
            .criterion-header {
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #f8f9fa;
                border-bottom: 1px solid #ddd;
            }
            .criterion-badge {
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            .badge-aa { background-color: #dee2e6; color: #212529; }
            .badge-aaa { background-color: #adb5bd; color: #212529; }

            .criterion-body {
                padding: 15px;
            }

            .issue-list {
                margin-top: 15px;
            }
            .issue-item {
                border-left: 4px solid #f9dede;
                padding: 10px;
                margin-bottom: 10px;
                background-color: #f8f9fa;
            }

            .status-passed { color: #28a745; }
            .status-failed { color: #dc3545; }
            .status-warning { color: #ffc107; }

            .info-box {
                background-color: #e1f3f8;
                padding: 15px;
                border-radius: 5px;
                margin-top: 10px;
            }

            details {
                margin-top: 10px;
            }
            summary {
                cursor: pointer;
                padding: 8px;
                background-color: #f8f9fa;
            }

            code {
                font-family: monospace;
                background-color: #f8f9fa;
                padding: 2px 5px;
                border-radius: 3px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th, td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
            th {
                background-color: #f8f9fa;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>WCAG 2.2 Accessibility Report</h1>
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
                            <h3>Criteria Tested</h3>
                            <p>{{ results.summary.criteria_tested }}</p>
                        </div>
                        <div class="summary-item passed">
                            <h3>Criteria Passed</h3>
                            <p>{{ results.summary.criteria_passed }}</p>
                        </div>
                        <div class="summary-item failed">
                            <h3>Criteria Failed</h3>
                            <p>{{ results.summary.criteria_failed }}</p>
                        </div>
                        <div class="summary-item warning">
                            <h3>Manual Checks Required</h3>
                            <p>{{ results.summary.manual_checks_required }}</p>
                        </div>
                    </div>
                </section>

                <section>
                    <h2>WCAG 2.2 Criteria Results</h2>

                    {% for criterion_id, criterion_results in results.results.items() %}
                        <div class="criterion-card">
                            <div class="criterion-header">
                                <div>
                                    <h3>{{ criterion_id }}: {{ criterion_results.name }}</h3>
                                    <span class="criterion-badge badge-{{ criterion_results.level|lower }}">
                                        Level {{ criterion_results.level }}
                                    </span>
                                </div>
                                <div>
                                    {% if criterion_results.passed %}
                                        <span class="status-passed">✓ Passed</span>
                                    {% else %}
                                        <span class="status-failed">✗ Failed</span>
                                    {% endif %}

                                    {% if criterion_results.manual_check_required %}
                                        <span class="status-warning"> • Manual check required</span>
                                    {% endif %}
                                </div>
                            </div>

                            <div class="criterion-body">
                                <p><strong>Description:</strong> {{ criterion_results.description }}</p>

                                {% if criterion_results.summary %}
                                    <p><strong>Summary:</strong> {{ criterion_results.summary }}</p>
                                {% endif %}

                                {% if criterion_results.manual_check_required %}
                                    <div class="info-box">
                                        <p><strong>Note:</strong> {{ criterion_results.manual_check_instructions }}</p>
                                    </div>
                                {% endif %}

                                {% if criterion_results.help_mechanisms %}
                                    <details>
                                        <summary>Help Mechanisms Found ({{ criterion_results.help_mechanisms|length }})</summary>
                                        <table>
                                            <tr>
                                                <th>Type</th>
                                                <th>Text</th>
                                                <th>Element</th>
                                            </tr>
                                            {% for mechanism in criterion_results.help_mechanisms %}
                                                <tr>
                                                    <td>{{ mechanism.help_type }}</td>
                                                    <td>{{ mechanism.element_info.text }}</td>
                                                    <td><code>{{ mechanism.element }}{% if mechanism.element_info.id %} id="{{ mechanism.element_info.id }}"{% endif %}</code></td>
                                                </tr>
                                            {% endfor %}
                                        </table>
                                    </details>
                                {% endif %}

                                {% if criterion_results.issues %}
                                    <div class="issue-list">
                                        <h4>Issues ({{ criterion_results.issues|length }})</h4>

                                        {% for issue in criterion_results.issues %}
                                            <div class="issue-item">
                                                <p><strong>Message:</strong> {{ issue.message }}</p>
                                                <p><strong>Element:</strong> <code>{{ issue.element }}{% if issue.element_info.id %} id="{{ issue.element_info.id }}"{% endif %}{% if issue.element_info.class %} class="{{ issue.element_info.class }}"{% endif %}</code></p>

                                                {% if issue.size %}
                                                    <p><strong>Size:</strong> Width: {{ issue.size.width }}, Height: {{ issue.size.height }}</p>
                                                {% endif %}

                                                {% if issue.fields %}
                                                    <details>
                                                        <summary>Field Details</summary>
                                                        <table>
                                                            <tr>
                                                                <th>Type</th>
                                                                <th>Name</th>
                                                                <th>ID</th>
                                                            </tr>
                                                            {% for field in issue.fields %}
                                                                <tr>
                                                                    <td>{{ field.type }}</td>
                                                                    <td>{{ field.name }}</td>
                                                                    <td>{{ field.id }}</td>
                                                                </tr>
                                                            {% endfor %}
                                                        </table>
                                                    </details>
                                                {% endif %}

                                                {% if issue.cognitive_tests %}
                                                    <p><strong>Cognitive Tests:</strong> 
                                                    {% for test_type, present in issue.cognitive_tests.items() %}
                                                        {% if present %}{{ test_type|replace('_', ' ')|title }}{% if not loop.last %}, {% endif %}{% endif %}
                                                    {% endfor %}
                                                    </p>
                                                {% endif %}
                                            </div>
                                        {% endfor %}
                                    </div>
                                {% endif %}
                            </div>
                        </div>
                    {% endfor %}
                </section>
            {% endif %}
        </div>
    </body>
    </html>
        """

        # Render the template with the results
        from jinja2 import Template
        return Template(template_str).render(results=results)

    def _parse_pixel_value(self, value):
        """Parse a CSS pixel value string and return a float."""
        if not value or not isinstance(value, str):
            return 0

        try:
            return float(value.replace('px', ''))
        except (ValueError, TypeError):
            return 0