"""
UI module for the Accessibility Tester application.
Provides a graphical user interface using Flet.
"""
import traceback
from datetime import datetime
import os
import uuid

import flet as ft
import subprocess
import platform
from flet import Page, TextField, ElevatedButton, Text, ProgressBar, Column, SnackBar
import logging

from utils.report_generators import generate_enhanced_summary_report
from ..core.test_orchestrator import AccessibilityTestOrchestrator
from ..config.config_manager import ConfigManager
from ..utils.crawler import WebsiteCrawler
from .browser_testing_helper import BrowserTestingManager, ScreenSize


class AccessibilityTesterUI:
    """Main UI for the accessibility tester."""

    def __init__(self, page: Page):
        self.url_checkboxes = []
        self.browser_checkboxes = {}
        self.screen_size_controls = []
        self.page = page
        self.setup_page_properties()

        # Initialize backend components
        self.orchestrator = None
        self.config_manager = ConfigManager()
        self.config_manager.initialize_wave_api()

        # Initialize UI components
        self.setup_snackbar()
        self.create_url_input()
        self.create_tool_selection()
        self.create_japanese_controls()
        self.create_crawl_options()

        # Create browser and screen size controls
        self.browser_screen_container = None  # Will be created later

        self.create_action_buttons()
        self.create_results_container()
        self.create_page_selection_dialog()

        # Build the UI
        self.setup_ui()

        # Logger
        self.logger = logging.getLogger(self.__class__.__name__)

        # Store crawled URLs
        self.crawled_urls = []
        self.last_report_dir = None

    def setup_page_properties(self):
        """Setup page properties."""
        self.page.title = "Accessibility Tester"
        self.page.window_width = 1000
        self.page.window_height = 900
        self.page.window_resizable = True
        self.page.padding = 20
        self.page.scroll = "auto"

    def setup_snackbar(self):
        """Setup snackbar for notifications."""
        self.snack_bar = ft.SnackBar(
            content=ft.Text(""),
            action="Dismiss"
        )
        self.page.overlay.append(self.snack_bar)

    def show_snackbar(self, message):
        """Show a snackbar message."""
        self.snack_bar.content = ft.Text(message)
        self.snack_bar.open = True
        self.page.update()

    def create_url_input(self):
        """Create URL input field."""
        self.url_input = TextField(
            label="Website URL",
            hint_text="https://www.example.com",
            width=600,
            prefix_icon=ft.icons.LINK
        )

    def create_tool_selection(self):
        """Create tool selection controls."""
        self.axe_checkbox = ft.Checkbox(label="Axe (Default)", value=True)
        self.wave_checkbox = ft.Checkbox(label="WAVE API (Requires API key)")
        self.lighthouse_checkbox = ft.Checkbox(label="Lighthouse")
        self.pa11y_checkbox = ft.Checkbox(label="Pa11y")
        self.htmlcs_checkbox = ft.Checkbox(label="HTML CodeSniffer")
        self.wcag22_checkbox = ft.Checkbox(label="WCAG 2.2 Custom Tests")

        # API Key input for WAVE
        self.wave_api_key_input = TextField(
            label="WAVE API Key",
            hint_text="Enter your WAVE API key",
            width=400,
            password=True,
            visible=False
        )

        # Show/hide API key input based on checkbox
        def wave_checkbox_changed(e):
            self.wave_api_key_input.visible = self.wave_checkbox.value
            self.page.update()

        self.wave_checkbox.on_change = wave_checkbox_changed

        # W3C Tools main checkbox
        self.w3c_checkbox = ft.Checkbox(label="W3C Accessibility Tools", value=False)

        # W3C sub-test checkboxes
        self.w3c_html_validator_checkbox = ft.Checkbox(
            label="HTML Validator",
            value=True,
            visible=False
        )
        self.w3c_css_validator_checkbox = ft.Checkbox(
            label="CSS Validator",
            value=True,
            visible=False
        )
        self.w3c_link_checker_checkbox = ft.Checkbox(
            label="Link Checker",
            value=True,
            visible=False
        )
        self.w3c_nu_validator_checkbox = ft.Checkbox(
            label="Nu HTML Checker (requires Java)",
            value=False,
            visible=False
        )
        self.w3c_aria_validator_checkbox = ft.Checkbox(
            label="ARIA Validator",
            value=True,
            visible=False
        )
        self.w3c_dom_validator_checkbox = ft.Checkbox(
            label="DOM Accessibility",
            value=True,
            visible=False
        )

        # Container for W3C sub-tests
        self.w3c_subtests_container = ft.Container(
            content=ft.Column([
                ft.Text("Select W3C Tests:", size=14, italic=True),
                self.w3c_html_validator_checkbox,
                self.w3c_css_validator_checkbox,
                self.w3c_link_checker_checkbox,
                self.w3c_nu_validator_checkbox,
                self.w3c_aria_validator_checkbox,
                self.w3c_dom_validator_checkbox,
            ]),
            padding=ft.padding.only(left=30, top=5, bottom=5),
            visible=False
        )

        # Toggle W3C sub-tests visibility when the main checkbox changes
        def w3c_checkbox_changed(e):
            # self.w3c_subtests_container.visible = self.w3c_checkbox.value
            # self.page.update()
            # Update container visibility
            self.w3c_subtests_container.visible = self.w3c_checkbox.value

            # Also update individual checkbox visibility
            self.w3c_html_validator_checkbox.visible = self.w3c_checkbox.value
            self.w3c_css_validator_checkbox.visible = self.w3c_checkbox.value
            self.w3c_link_checker_checkbox.visible = self.w3c_checkbox.value
            self.w3c_nu_validator_checkbox.visible = self.w3c_checkbox.value
            self.w3c_aria_validator_checkbox.visible = self.w3c_checkbox.value
            self.w3c_dom_validator_checkbox.visible = self.w3c_checkbox.value

            # Make sure to update the page
            self.page.update()

        self.w3c_checkbox.on_change = w3c_checkbox_changed

        # Tools container
        self.tools_container = ft.Container(
            content=ft.Column([
                ft.Text("Select Testing Tools:", size=16, weight=ft.FontWeight.BOLD),
                self.axe_checkbox,
                self.wave_checkbox,
                self.wave_api_key_input,
                self.lighthouse_checkbox,
                self.pa11y_checkbox,
                self.htmlcs_checkbox,
                self.w3c_checkbox,
                self.w3c_subtests_container,  # Add the sub-tests container here
                self.wcag22_checkbox,
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            margin=ft.margin.only(top=20)
        )

    def create_japanese_controls(self):
        """Create Japanese-specific testing controls."""
        self.japanese_checkbox = ft.Checkbox(label="Enable Japanese Accessibility Testing", value=False)
        self.form_zero_checkbox = ft.Checkbox(label="Enable Form Zero Testing", value=False)
        self.ruby_checkbox = ft.Checkbox(label="Check Ruby Text (Furigana)", value=True)

        # Encoding options
        self.encoding_dropdown = ft.Dropdown(
            label="Preferred Encoding",
            options=[
                ft.dropdown.Option("utf-8", "UTF-8"),
                ft.dropdown.Option("shift_jis", "Shift JIS"),
                ft.dropdown.Option("euc-jp", "EUC-JP"),
            ],
            value="utf-8",
            width=200
        )

        # Japanese controls container
        self.japanese_container = ft.Container(
            content=ft.Column([
                ft.Text("Japanese Accessibility Options:", size=16, weight=ft.FontWeight.BOLD),
                self.japanese_checkbox,
                self.form_zero_checkbox,
                self.ruby_checkbox,
                self.encoding_dropdown
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            margin=ft.margin.only(top=20),
            visible=False
        )

        # Show/hide Japanese options
        def japanese_checkbox_changed(e):
            self.japanese_container.visible = self.japanese_checkbox.value
            self.page.update()

        self.japanese_checkbox.on_change = japanese_checkbox_changed

    def create_crawl_options(self):
        """Create website crawling options."""
        self.crawl_checkbox = ft.Checkbox(label="Crawl website", value=False)
        self.max_pages_input = ft.TextField(
            label="Maximum pages",
            value="10",
            width=100,
            keyboard_type="number",
            visible=False
        )
        self.same_domain_checkbox = ft.Checkbox(
            label="Stay on same domain",
            value=True,
            visible=False
        )

        # Crawl options container
        self.crawl_container = ft.Container(
            content=ft.Column([
                ft.Text("Crawling Options:", size=16, weight=ft.FontWeight.BOLD),
                self.crawl_checkbox,
                ft.Row([
                    self.max_pages_input,
                    self.same_domain_checkbox
                ])
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            margin=ft.margin.only(top=20)
        )

        # Show/hide crawling options
        def crawl_checkbox_changed(e):
            self.max_pages_input.visible = self.crawl_checkbox.value
            self.same_domain_checkbox.visible = self.crawl_checkbox.value
            self.page.update()

        self.crawl_checkbox.on_change = crawl_checkbox_changed

    def create_action_buttons(self):
        """Create action buttons."""
        self.test_button = ElevatedButton(
            text="Run Accessibility Tests",
            icon=ft.icons.PLAY_ARROW,
            on_click=self.run_tests
        )

        self.cancel_button = ElevatedButton(
            text="Cancel",
            icon=ft.icons.CANCEL,
            on_click=self.cancel_tests,
            visible=False
        )

        self.settings_button = ElevatedButton(
            text="Settings",
            icon=ft.icons.SETTINGS,
            on_click=self.open_settings
        )

        self.open_reports_button = ElevatedButton(
            text="Open Reports Folder",
            icon=ft.icons.FOLDER_OPEN,
            on_click=self.open_reports_folder,
            visible=False
        )

        self.buttons_row = ft.Row([
            self.test_button,
            self.cancel_button,
            self.settings_button,
            self.open_reports_button
        ])

    def create_results_container(self):
        """Create container for test results."""
        self.progress_bar = ProgressBar(visible=False)
        self.status_text = Text("Ready to test")

        self.results_text = ft.Text(
            size=14,
            selectable=True
        )

        self.results_container = ft.Container(
            content=ft.Column([
                ft.Text("Results:", size=16, weight=ft.FontWeight.BOLD),
                self.progress_bar,
                self.status_text,
                ft.Container(height=10),  # Spacer
                self.results_text
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            margin=ft.margin.only(top=20),
            visible=False
        )

    def create_page_selection_dialog(self):
        """Initialize page selection dialog components."""
        self.select_all_checkbox = None

    def toggle_all_urls(self, e):
        """Toggle selection state for all URLs."""
        for checkbox in self.url_checkboxes:
            checkbox.value = self.select_all_checkbox.value
        self.page.update()

    def setup_ui(self):
        """Arrange UI components."""
        print("Setting up UI components")  # Debug print

        # Create browser and screen size controls
        if self.browser_screen_container is None:
            print("Creating browser screen controls")  # Debug print
            self.browser_screen_container = self.create_browser_screen_controls()
        else:
            print("Browser screen controls already exist")  # Debug print

        self.page.add(
            ft.Text("Accessibility Tester", size=24, weight=ft.FontWeight.BOLD),
            self.url_input,
            self.tools_container,
            self.japanese_checkbox,
            self.japanese_container,
            self.crawl_container,
            self.browser_screen_container,  # Add the new controls
            self.buttons_row,
            self.results_container
        )

        print("UI components added to page")  # Debug print
        self.page.update()
        print("Page updated")  # Debug print

    def set_orchestrator(self, orchestrator):
        """Set the test orchestrator.

        Args:
            orchestrator (AccessibilityTestOrchestrator): The test orchestrator
        """
        self.orchestrator = orchestrator

    def update_w3c_subtests(self):
        """Update the W3C tester with the currently selected sub-tests."""
        if not self.w3c_checkbox.value:
            return

        # Collect enabled sub-tests
        w3c_subtests = []

        if hasattr(self, 'w3c_html_validator_checkbox') and self.w3c_html_validator_checkbox.value:
            w3c_subtests.append("html_validator")
        if hasattr(self, 'w3c_css_validator_checkbox') and self.w3c_css_validator_checkbox.value:
            w3c_subtests.append("css_validator")
        if hasattr(self, 'w3c_link_checker_checkbox') and self.w3c_link_checker_checkbox.value:
            w3c_subtests.append("link_checker")
        if hasattr(self, 'w3c_nu_validator_checkbox') and self.w3c_nu_validator_checkbox.value:
            w3c_subtests.append("nu_validator")
        if hasattr(self, 'w3c_aria_validator_checkbox') and self.w3c_aria_validator_checkbox.value:
            w3c_subtests.append("aria_validator")
        if hasattr(self, 'w3c_dom_validator_checkbox') and self.w3c_dom_validator_checkbox.value:
            w3c_subtests.append("dom_accessibility")

        # Get the W3C tester from the orchestrator and set its enabled tests
        if self.orchestrator and "w3c_tools" in self.orchestrator.testers:
            w3c_tester = self.orchestrator.testers["w3c_tools"]
            w3c_tester.enabled_tests = w3c_subtests

    def run_tests(self, e):
        """Run accessibility tests."""
        # Validate input
        url = self.url_input.value
        if not url:
            self.show_snackbar("Please enter a URL")
            return

        # Add http:// prefix if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.value = url

        # Get selected tools
        selected_tools = []
        if self.axe_checkbox.value:
            selected_tools.append("axe")

        # For W3C tools, collect the enabled sub-tests
        w3c_enabled_subtests = None
        if self.w3c_checkbox.value:
            w3c_enabled_subtests = []
            if self.w3c_html_validator_checkbox.value:
                w3c_enabled_subtests.append("html_validator")
            if self.w3c_css_validator_checkbox.value:
                w3c_enabled_subtests.append("css_validator")
            if self.w3c_link_checker_checkbox.value:
                w3c_enabled_subtests.append("link_checker")
            if self.w3c_nu_validator_checkbox.value:
                w3c_enabled_subtests.append("nu_validator")
            if self.w3c_aria_validator_checkbox.value:
                w3c_enabled_subtests.append("aria_validator")
            if self.w3c_dom_validator_checkbox.value:
                w3c_enabled_subtests.append("dom_accessibility")

            # Store the enabled sub-tests for use during testing
            self.w3c_enabled_subtests = w3c_enabled_subtests
            selected_tools.append("w3c_tools")

        if self.wave_checkbox.value:
            if not self.wave_api_key_input.value:
                self.show_snackbar("Please enter a WAVE API key")
                return
            # Save WAVE API key
            self.config_manager.set_api_key("wave", self.wave_api_key_input.value)
            selected_tools.append("wave")
        if self.lighthouse_checkbox.value:
            selected_tools.append("lighthouse")
        if self.pa11y_checkbox.value:
            selected_tools.append("pa11y")
        if self.htmlcs_checkbox.value:
            selected_tools.append("htmlcs")
        if self.japanese_checkbox.value:
            selected_tools.append("japanese_a11y")
        # For W3C tools, collect the enabled sub-tests
        # if self.w3c_checkbox.value:
        #     self.update_w3c_subtests()  # Call the method here
        #     selected_tools.append("w3c_tools")

        if self.wcag22_checkbox.value:
            selected_tools.append("wcag22")

        if not selected_tools:
            self.show_snackbar("Please select at least one testing tool")
            return

        if not self.orchestrator:
            self.show_snackbar("Test orchestrator not initialized")
            return

        # Update UI state
        self.progress_bar.visible = True
        self.results_container.visible = True
        self.status_text.value = "Running tests..."
        self.test_button.disabled = True
        self.cancel_button.visible = True
        self.page.update()

        # If crawling is enabled, get all URLs and show selection dialog
        urls_to_test = [url]
        if self.crawl_checkbox.value:
            try:
                max_pages = int(self.max_pages_input.value)
                self.status_text.value = "Crawling website..."
                self.page.update()

                crawler = WebsiteCrawler(
                    max_pages=max_pages,
                    same_domain_only=self.same_domain_checkbox.value
                )
                self.crawled_urls = crawler.crawl(url)

                self.status_text.value = f"Found {len(self.crawled_urls)} pages. Select pages to test."
                self.page.update()

                # Show page selection dialog
                self.show_page_selection_dialog(self.crawled_urls, selected_tools)
                return

            except Exception as e:
                self.logger.error(f"Error crawling website: {str(e)}")
                self.show_snackbar(f"Error crawling website: {str(e)}")
                urls_to_test = [url]

        # Get enabled browsers and screen sizes
        enabled_browsers = self.get_enabled_browsers()
        if not enabled_browsers:
            self.show_snackbar("Please select at least one browser")
            return

        enabled_screen_sizes = self.get_enabled_screen_sizes()
        if not enabled_screen_sizes:
            self.show_snackbar("Please select at least one screen size")
            return

        # Convert screen sizes to the format expected by the orchestrator
        screen_sizes = [
            (size["name"], size["width"], size["height"])
            for size in enabled_screen_sizes
        ]

        # Save browser settings
        self.save_browser_settings()

        # If not crawling, proceed with direct testing
        # self._execute_tests(urls_to_test, selected_tools)
        self._execute_multi_browser_tests(urls_to_test, selected_tools, enabled_browsers, screen_sizes)

    def _execute_multi_browser_tests(self, urls, selected_tools, browsers, screen_sizes):
        """Execute tests across multiple browsers and screen sizes."""
        # Update status
        self.status_text.value = f"Testing {len(urls)} pages across {len(browsers)} browsers and {len(screen_sizes)} screen sizes..."
        self.page.update()

        try:
            base_dir = os.path.join(os.getcwd(), "Reports")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            test_id = f"report_{timestamp}_{uuid.uuid4().hex[:8]}"
            main_test_dir = os.path.join(base_dir, test_id)
            os.makedirs(main_test_dir, exist_ok=True)

            # Store the report directory for "Open Reports" button
            self.last_report_dir = main_test_dir

            all_results = {
                "timestamp": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
                "tools": selected_tools,
                "browsers": browsers,
                "screen_sizes": screen_sizes,
                "urls": {},
            }

            for url in urls:
                url_dir = os.path.join(main_test_dir, url
                                       .replace('https://', '')
                                       .replace('http://', '')
                                       .replace('/', '_')
                                       .replace(':', '_'))
                os.makedirs(url_dir, exist_ok=True)

                # Use multi-browser testing
                all_results["urls"][url] = self.orchestrator.run_multi_browser_tests(
                    url,
                    selected_tools,
                    screen_sizes,
                    browsers,
                    test_dir=url_dir,
                    w3c_subtests=self.w3c_enabled_subtests if hasattr(self, 'w3c_enabled_subtests') else None
                )

            # Generate enhanced summary report with browser comparison
            summary_path = generate_enhanced_summary_report(all_results, main_test_dir)
            self.logger.info(f"Saved Enhanced Summary Report to '{summary_path}'")

            # Display completion message
            self.status_text.value = "Testing complete"
            self.results_text.value = (
                f"Tested {len(urls)} pages with {len(selected_tools)} tools\n"
                f"Across {len(browsers)} browsers and {len(screen_sizes)} screen sizes"
            )

            # Show the path to the reports
            self.results_text.value += f"\n\nReports saved in: {main_test_dir}"
            # Show the "Open Reports" button
            self.open_reports_button.visible = True

        except Exception as e:
            self.logger.error(f"Error running tests: {traceback.format_exc()}")
            self.status_text.value = f"Error: {str(e)}"

        # Reset UI state
        self.progress_bar.visible = False
        self.test_button.disabled = False
        self.cancel_button.visible = False
        self.page.update()

    def show_page_selection_dialog(self, urls, selected_tools):
        """Show dialog to select which pages to test using overlay.

        Args:
            urls (list): List of URLs found by crawler
            selected_tools (list): Selected testing tools
        """
        self.logger.info(f"Showing URL selection with {len(urls)} URLs")

        # Reset checkbox list
        self.url_checkboxes = []

        # Create content for URL list
        url_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            height=400,
        )

        # Add the "Select All" checkbox
        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            value=True,
            on_change=self.toggle_all_urls
        )
        url_list.controls.append(self.select_all_checkbox)

        url_list.controls.append(ft.Divider())

        # Add a checkbox for each URL
        for i, url in enumerate(urls):
            url_checkbox = ft.Checkbox(
                label=url,
                value=True
            )
            self.url_checkboxes.append(url_checkbox)
            url_list.controls.append(url_checkbox)
            print(f"Added URL checkbox {i + 1}: {url[:50]}...")

        # Create functions for buttons
        def close_dialog(e):
            print("URL selection closed")  # Debug print
            self.page.overlay.remove(url_selection_overlay)

            # Re-enable test button
            self.test_button.disabled = False
            self.cancel_button.visible = False
            self.status_text.value = "Ready to test"
            self.progress_bar.visible = False

            self.page.update()

        def start_testing(e):
            print("Starting tests with selected URLs")

            # Get selected URLs
            selected_urls = [
                checkbox.label
                for checkbox in self.url_checkboxes
                if checkbox.value
            ]

            print(f"Selected {len(selected_urls)} URLs out of {len(urls)} total")

            # Remove the overlay AFTER getting the selected URLs
            self.page.overlay.remove(url_selection_overlay)
            self.page.update()

            if not selected_urls:
                self.show_snackbar("No pages selected for testing")

                # Reset UI state
                self.test_button.disabled = False
                self.cancel_button.visible = False
                self.status_text.value = "Ready to test"
                self.progress_bar.visible = False

                self.page.update()
                return

            # Update status
            self.status_text.value = f"Testing {len(selected_urls)} pages..."
            self.page.update()

            # Run tests on selected URLs
            self._execute_tests(selected_urls, selected_tools)

        # Create an overlay with a card for URL selection
        url_selection_overlay = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"Select Pages to Test ({len(urls)} found)", size=20, weight="bold"),
                            ft.IconButton(
                                icon=ft.icons.CLOSE,
                                on_click=close_dialog
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        ft.Divider(),

                        url_list,

                        ft.Row([
                            ft.OutlinedButton(text="Cancel", on_click=close_dialog),
                            ft.FilledButton(text="Test Selected", on_click=start_testing),
                        ], alignment=ft.MainAxisAlignment.END)
                    ]),
                    padding=20,
                    width=600,
                ),
            ),
            alignment=ft.alignment.center,
            width=self.page.width,
            height=self.page.height,
            bgcolor=ft.colors.with_opacity(0.75, ft.colors.BLACK),
        )

        # Add the overlay to the page
        self.page.overlay.append(url_selection_overlay)
        print("URL selection overlay added")  # Debug print
        self.page.update()

    def _execute_tests(self, urls, selected_tools):
        """Execute tests on the given URLs.

        Args:
            urls (list): List of URLs to test
            selected_tools (list): Selected testing tools
        """
        # Configure Japanese testing if enabled
        if self.japanese_checkbox.value:
            self.orchestrator.configure_japanese_testing(
                enabled=True,
                form_zero=self.form_zero_checkbox.value,
                ruby_check=self.ruby_checkbox.value,
                encoding=self.encoding_dropdown.value
            )

        # Update status
        self.status_text.value = f"Testing {len(urls)} pages..."
        self.page.update()

        try:
            # Run batch test
            if len(urls) > 1:
                all_results = self.orchestrator.batch_test_urls(urls, selected_tools)
                # Get the main test directory from the results
                if all_results and next(iter(all_results.values())):
                    first_result = next(iter(all_results.values()))
                    first_tool = next(iter(first_result.values()))
                    self.last_report_dir = os.path.dirname(os.path.dirname(first_tool.get("test_dir", "")))
            else:
                # Run single test
                results = self.orchestrator.run_tests(
                    urls[0],
                    selected_tools,
                    w3c_subtests=self.w3c_enabled_subtests if hasattr(self, 'w3c_enabled_subtests') else None
                )

                # Store the report directory for the "Open Reports" button
                if results and next(iter(results.values())):
                    first_tool = next(iter(results.values()))
                    self.last_report_dir = first_tool.get("test_dir", "")

            # Display completion message
            self.status_text.value = "Testing complete"
            self.results_text.value = f"Tested {len(urls)} pages with {len(selected_tools)} tools"

            # Show the path to the reports
            if self.last_report_dir:
                self.results_text.value += f"\n\nReports saved in: {self.last_report_dir}"
                # Show the "Open Reports" button
                self.open_reports_button.visible = True

        except Exception as e:
            self.logger.error(f"Error running tests: {str(e)}")
            self.status_text.value = f"Error: {str(e)}"

        # Reset UI state
        self.progress_bar.visible = False
        self.test_button.disabled = False
        self.cancel_button.visible = False
        self.page.update()

    def cancel_tests(self, e):
        """Cancel running tests."""
        # TODO: Implement test cancellation
        self.status_text.value = "Tests cancelled"
        self.progress_bar.visible = False
        self.test_button.disabled = False
        self.cancel_button.visible = False
        self.page.update()

    def open_reports_folder(self, e):
        """Open the reports folder in the file explorer."""
        if self.last_report_dir and os.path.exists(self.last_report_dir):
            try:
                # Open folder based on the operating system
                if platform.system() == "Windows":
                    os.startfile(self.last_report_dir)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", self.last_report_dir], check=True)
                else:  # Linux
                    subprocess.run(["xdg-open", self.last_report_dir], check=True)

                self.logger.info(f"Opened reports folder: {self.last_report_dir}")
            except Exception as e:
                self.logger.error(f"Error opening reports folder: {str(e)}")
                self.show_snackbar(f"Error opening reports folder: {str(e)}")
        else:
            self.show_snackbar("No report directory available")

    def open_settings(self, e):
        """Open settings dialog."""
        print("Opening settings dialog")  # Debug print

        # Get current settings
        general_settings = self.config_manager.get_general_settings()

        # Create settings form
        report_dir_input = ft.TextField(
            label="Report Directory",
            value=general_settings.get("report_dir", "Reports"),
            width=300
        )

        screenshot_checkbox = ft.Checkbox(
            label="Take screenshots of violations",
            value=general_settings.get("screenshot_on_violation", True)
        )

        combined_report_checkbox = ft.Checkbox(
            label="Generate combined report",
            value=general_settings.get("combined_report", True)
        )

        # Create settings overlay container for reference
        settings_overlay = ft.Container()

        # Create functions for buttons
        def close_dialog(e):
            print("Settings dialog closed with Close/Cancel")  # Debug print
            try:
                if settings_overlay in self.page.overlay:
                    self.page.overlay.remove(settings_overlay)
                    self.page.update()
                    print("Settings overlay successfully removed")
                else:
                    print("Settings overlay not found in page overlays")
            except Exception as ex:
                print(f"Error closing settings: {ex}")

        def save_settings(e):
            print("Saving settings")  # Debug print
            try:
                # Save settings to config
                general_settings = self.config_manager.get_general_settings()
                general_settings["report_dir"] = report_dir_input.value
                general_settings["screenshot_on_violation"] = screenshot_checkbox.value
                general_settings["combined_report"] = combined_report_checkbox.value

                self.config_manager.save_config()
                self.show_snackbar("Settings saved")

                # Remove the overlay
                if settings_overlay in self.page.overlay:
                    self.page.overlay.remove(settings_overlay)
                    self.page.update()
                    print("Settings overlay removed after save")
                else:
                    print("Settings overlay not found after save")
            except Exception as ex:
                print(f"Error saving settings: {ex}")

        # Create an overlay with a card for settings
        settings_overlay = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Settings", size=20, weight="bold"),
                            ft.IconButton(
                                icon=ft.icons.CLOSE,
                                on_click=close_dialog
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                        ft.Divider(),

                        ft.Text("General Settings", size=16, weight="bold"),
                        report_dir_input,
                        screenshot_checkbox,
                        combined_report_checkbox,

                        ft.Container(height=20),  # Spacer

                        ft.Row([
                            ft.OutlinedButton(text="Cancel", on_click=close_dialog),
                            ft.FilledButton(text="Save", on_click=save_settings),
                        ], alignment=ft.MainAxisAlignment.END)
                    ]),
                    padding=20,
                    width=400,
                ),
            ),
            alignment=ft.alignment.center,
            width=self.page.width,
            height=self.page.height,
            bgcolor=ft.colors.with_opacity(0.75, ft.colors.BLACK),
        )

        # Add the overlay to the page
        self.page.overlay.append(settings_overlay)
        print("Settings overlay added")  # Debug print
        self.page.update()

    def toggle_japanese_testing(self, visible=False):
        """Toggle visibility of Japanese testing options.

        Args:
            visible (bool): Whether to show Japanese testing options
        """
        # Hide Japanese options in UI
        self.japanese_checkbox.visible = visible
        self.japanese_container.visible = False

        # Update the page
        self.page.update()

    """
    Updates to the UI module to support multi-browser and multi-screen size testing.
    """

    def create_browser_screen_controls(self):
        """Create browser and screen size controls."""
        # Load browser settings from config
        browser_settings = self.config_manager.get_browser_settings()

        print(f"Browser settings: {browser_settings}")  # Debug print

        # Browser selection section
        browser_heading = ft.Text("Browser Settings:", size=16, weight=ft.FontWeight.BOLD)

        # Create browser checkboxes
        browser_list = ft.Column(spacing=5)

        # Add predefined browsers
        default_browsers = [
            {"name": "Chrome", "enabled": True},
            {"name": "Firefox", "enabled": False},
            {"name": "Edge", "enabled": False},
            {"name": "Safari", "enabled": False}
        ]

        # Always ensure we have browsers to display by using default if list is empty
        browsers = browser_settings.get("browsers", [])
        if not browsers:  # If browsers list is empty, use defaults
            browsers = default_browsers
            print("Using default browsers list as config is empty")

        print(f"Browsers to display: {browsers}")  # Debug print
        browsers = browser_settings["browsers"]

        for browser in browsers:
            browser_name = browser.get("name")
            checkbox = ft.Checkbox(
                label=browser_name,
                value=browser.get("enabled", False)
            )
            self.browser_checkboxes[browser_name] = checkbox
            browser_list.controls.append(checkbox)

            print(f"Added checkbox for {browser_name}")  # Debug print

        print(f"{browser_list.controls}: {len(browser_list.controls)}")

        # Screen size selection section
        screen_size_heading = ft.Text("Screen Sizes:", size=16, weight=ft.FontWeight.BOLD)

        # Create screen size items with width/height inputs
        screen_size_list = ft.Column(spacing=10)


        # Add predefined screen sizes
        default_sizes = [
            {"name": "Mobile", "width": 375, "height": 667, "enabled": True},
            {"name": "Tablet", "width": 768, "height": 1024, "enabled": True},
            {"name": "Desktop", "width": 1366, "height": 768, "enabled": True}
        ]

        # Always ensure we have screen sizes to display by using default if list is empty
        screen_sizes = browser_settings.get("screen_sizes", [])
        if not screen_sizes:  # If screen_sizes list is empty, use defaults
            screen_sizes = default_sizes
            print("Using default screen sizes list as config is empty")

        print(f"Screen sizes to display: {screen_sizes}")  # Debug print

        screen_sizes = browser_settings["screen_sizes"]

        for size in screen_sizes:
            size_row = ft.Row([
                ft.Checkbox(
                    label=size.get("name", "Unknown"),
                    value=size.get("enabled", True)
                ),
                ft.Text("W:"),
                ft.TextField(
                    value=str(size.get("width", 1366)),
                    width=70,
                    keyboard_type="number"
                ),
                ft.Text("H:"),
                ft.TextField(
                    value=str(size.get("height", 768)),
                    width=70,
                    keyboard_type="number"
                )
            ], alignment=ft.MainAxisAlignment.START, spacing=5)

            self.screen_size_controls.append({
                "name": size.get("name"),
                "checkbox": size_row.controls[0],
                "width": size_row.controls[2],
                "height": size_row.controls[4]
            })

            screen_size_list.controls.append(size_row)
            print(f"Added controls for screen size {size.get('name')}")  # Debug print

        # Add button to add new screen size
        add_size_button = ft.ElevatedButton(
            text="Add Custom Size",
            icon=ft.icons.ADD,
            on_click=self.add_custom_screen_size
        )

        # Create and return the container
        browser_screen_container = ft.Container(
            content=ft.Column([
                browser_heading,
                browser_list,
                ft.Divider(),
                screen_size_heading,
                screen_size_list,
                add_size_button
            ]),
            padding=10,
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=5,
            margin=ft.margin.only(top=20)
        )

        print(f"Created browser screen container with {len(browser_list.controls)} browser checkboxes")
        print(f"Created browser screen container with {len(screen_size_list.controls)} screen size rows")

        return browser_screen_container

    def add_custom_screen_size(self, e):
        """Add a new custom screen size."""
        # Create dialog for adding a new size
        name_input = ft.TextField(label="Name", hint_text="Custom Size")
        width_input = ft.TextField(label="Width", value="1024", keyboard_type="number")
        height_input = ft.TextField(label="Height", value="768", keyboard_type="number")

        def add_size(e):
            """Add the new size and close the dialog."""
            try:
                # Validate inputs
                name = name_input.value.strip()
                width = int(width_input.value)
                height = int(height_input.value)

                if not name:
                    self.show_snackbar("Name is required")
                    return

                if width <= 0 or height <= 0:
                    self.show_snackbar("Width and height must be positive")
                    return

                # Create new size row
                size_row = ft.Row([
                    ft.Checkbox(
                        label=name,
                        value=True
                    ),
                    ft.Text("W:"),
                    ft.TextField(
                        value=str(width),
                        width=70,
                        keyboard_type="number"
                    ),
                    ft.Text("H:"),
                    ft.TextField(
                        value=str(height),
                        width=70,
                        keyboard_type="number"
                    )
                ], alignment=ft.MainAxisAlignment.START, spacing=5)

                # Add to controls
                self.screen_size_controls.append({
                    "name": name,
                    "checkbox": size_row.controls[0],
                    "width": size_row.controls[2],
                    "height": size_row.controls[4]
                })

                # Add to screen size list
                screen_size_list = self.browser_screen_container.content.controls[4]
                screen_size_list.controls.append(size_row)

                # Hide dialog
                dialog.open = False
                self.page.update()

            except ValueError:
                self.show_snackbar("Width and height must be numbers")

        # Create dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Add Custom Screen Size"),
            content=ft.Column([
                name_input,
                width_input,
                height_input
            ], spacing=10, tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, "open", False)),
                ft.TextButton("Add", on_click=add_size)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # Show dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def get_enabled_browsers(self):
        """Get list of enabled browsers."""
        return [
            name for name, checkbox in self.browser_checkboxes.items()
            if checkbox.value
        ]

    def get_enabled_screen_sizes(self):
        """Get list of enabled screen sizes."""
        return [
            {
                "name": control["name"],
                "width": int(control["width"].value),
                "height": int(control["height"].value)
            }
            for control in self.screen_size_controls
            if control["checkbox"].value
        ]

    def save_browser_settings(self):
        """Save browser and screen size settings to config."""
        # Get current settings
        browsers = [
            {"name": name, "enabled": checkbox.value}
            for name, checkbox in self.browser_checkboxes.items()
        ]

        screen_sizes = [
            {
                "name": control["name"],
                "width": int(control["width"].value),
                "height": int(control["height"].value),
                "enabled": control["checkbox"].value
            }
            for control in self.screen_size_controls
        ]

        # Update config
        self.config_manager.update_browser_settings({
            "browsers": browsers,
            "screen_sizes": screen_sizes
        })

    def _generate_enhanced_summary_report(self, all_results, main_test_dir):
        """Generate an enhanced summary report that compares results across browsers and screen sizes.

        Args:
            all_results (dict): All test results
            main_test_dir (str): Main test directory

        Returns:
            str: Path to the generated report
        """
        try:
            from jinja2 import Template

            template_str = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Enhanced Accessibility Report</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1, h2, h3, h4 { color: #2a4365; }
                    .summary { background-color: #f8f9fa; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
                    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .browser-nav { display: flex; gap: 10px; margin: 20px 0; }
                    .browser-tab { padding: 10px; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; }
                    .browser-tab.active { background-color: #e9ecef; font-weight: bold; }
                    .browser-content { display: none; }
                    .browser-content.active { display: block; }
                    .size-nav { display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0; }
                    .size-tab { padding: 8px; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; }
                    .size-tab.active { background-color: #e9ecef; font-weight: bold; }
                    .size-content { display: none; }
                    .size-content.active { display: block; }
                    .tool-header { background-color: #f8f9fa; padding: 10px; margin: 15px 0 10px; border-radius: 5px; }
                    .issue-list { margin-left: 20px; }
                    .issue-item { margin-bottom: 8px; padding-left: 10px; border-left: 3px solid #ddd; }
                    .status-good { color: #28a745; }
                    .status-warning { color: #ffc107; }
                    .status-error { color: #dc3545; }
                    .comparison-table th { position: sticky; top: 0; background-color: #f2f2f2; }
                    .url-section { margin-bottom: 30px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
                    .issue-count { font-weight: bold; }
                    .error-count { color: #dc3545; }
                    .warning-count { color: #ffc107; }
                    .notice-count { color: #17a2b8; }
                    .comparison-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
                    .comparison-card { border: 1px solid #ddd; border-radius: 5px; padding: 15px; }
                    .card-header { font-weight: bold; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
                    .toggle-button { margin-top: 10px; padding: 5px 10px; background-color: #f2f2f2; border: none; border-radius: 3px; cursor: pointer; }
                    .toggle-button:hover { background-color: #e9ecef; }
                    @media (max-width: 768px) {
                        .comparison-grid { grid-template-columns: 1fr; }
                    }
                </style>
            </head>
            <body>
                <h1>Enhanced Accessibility Report</h1>

                <div class="summary">
                    <h2>Summary</h2>
                    <p><strong>Date:</strong> {{ results.timestamp }}</p>
                    <p><strong>URLs Tested:</strong> {{ results.urls|length }}</p>
                    <p><strong>Browsers:</strong> {{ results.browsers|join(', ') }}</p>
                    <p><strong>Screen Sizes:</strong> 
                        {% for size in results.screen_sizes %}
                            {{ size[0] }} ({{ size[1] }}×{{ size[2] }}px){% if not loop.last %}, {% endif %}
                        {% endfor %}
                    </p>
                    <p><strong>Testing Tools:</strong> {{ results.tools|join(', ') }}</p>
                </div>

                <h2>Cross-Browser Comparison</h2>

                {% for url, url_data in results.urls.items() %}
                    <div class="url-section">
                        <h3>{{ url }}</h3>

                        <h4>Browser Comparison</h4>
                        <div class="comparison-grid">
                            {% for browser, browser_data in url_data.browsers.items() %}
                                <div class="comparison-card">
                                    <div class="card-header">{{ browser }}</div>

                                    {% set total_issues = [] %}
                                    {% for size_key, size_data in browser_data.screen_sizes.items() %}
                                        {% for tool, tool_data in size_data.tools.items() %}
                                            {% if tool == 'axe' and tool_data.violations %}
                                                {% set _ = total_issues.extend(tool_data.violations) %}
                                            {% elif tool == 'wave' and tool_data.categories.error %}
                                                {% set _ = total_issues.append(1) for _ in range(tool_data.categories.error.count) %}
                                            {% endif %}
                                        {% endfor %}
                                    {% endfor %}

                                    <p class="issue-count {% if total_issues|length > 0 %}error-count{% endif %}">
                                        Issues found: {{ total_issues|length }}
                                    </p>

                                    <button class="toggle-button" onclick="toggleDetails('{{ url|replace('.', '_') }}_{{ browser }}')">
                                        View Details
                                    </button>

                                    <div id="{{ url|replace('.', '_') }}_{{ browser }}" style="display: none; margin-top: 10px;">
                                        {% for size_key, size_data in browser_data.screen_sizes.items() %}
                                            <div style="margin-top: 10px; padding-top: 5px; border-top: 1px dashed #ddd;">
                                                <h5>{{ size_key }}</h5>
                                                {% for tool, tool_data in size_data.tools.items() %}
                                                    <div style="margin-left: 10px;">
                                                        <strong>{{ tool }}:</strong>

                                                        {% if tool == 'axe' %}
                                                            {{ tool_data.violations|length }} violations
                                                        {% elif tool == 'wave' %}
                                                            {{ tool_data.categories.error.count }} errors
                                                        {% else %}
                                                            {% if tool_data.error %}
                                                                Error: {{ tool_data.error }}
                                                            {% else %}
                                                                Completed
                                                            {% endif %}
                                                        {% endif %}
                                                    </div>
                                                {% endfor %}
                                            </div>
                                        {% endfor %}
                                    </div>
                                </div>
                            {% endfor %}
                        </div>

                        <h4>Screen Size Comparison</h4>
                        <table class="comparison-table">
                            <tr>
                                <th>Screen Size</th>
                                {% for browser in results.browsers %}
                                    <th>{{ browser }}</th>
                                {% endfor %}
                            </tr>
                            {% for size_name, width, height in results.screen_sizes %}
                                {% set size_key = size_name + '_' + width|string + 'x' + height|string %}
                                <tr>
                                    <td>{{ size_name }} ({{ width }}×{{ height }})</td>
                                    {% for browser in results.browsers %}
                                        <td>
                                            {% if url_data.browsers[browser] and url_data.browsers[browser].screen_sizes[size_key] %}
                                                {% set size_data = url_data.browsers[browser].screen_sizes[size_key] %}
                                                {% set issue_count = 0 %}

                                                {% for tool, tool_data in size_data.tools.items() %}
                                                    {% if tool == 'axe' and tool_data.violations %}
                                                        {% set issue_count = issue_count + tool_data.violations|length %}
                                                    {% elif tool == 'wave' and tool_data.categories.error %}
                                                        {% set issue_count = issue_count + tool_data.categories.error.count %}
                                                    {% endif %}
                                                {% endfor %}

                                                <span class="{% if issue_count > 10 %}status-error{% elif issue_count > 0 %}status-warning{% else %}status-good{% endif %}">
                                                    {{ issue_count }} issues
                                                </span>
                                            {% else %}
                                                N/A
                                            {% endif %}
                                        </td>
                                    {% endfor %}
                                </tr>
                            {% endfor %}
                        </table>
                    </div>
                {% endfor %}

                <script>
                    function toggleDetails(id) {
                        const element = document.getElementById(id);
                        if (element.style.display === "none") {
                            element.style.display = "block";
                        } else {
                            element.style.display = "none";
                        }
                    }
                </script>
            </body>
            </html>
            """

            html_report = Template(template_str).render(results=all_results)

            # Save HTML report
            output_path = os.path.join(main_test_dir, "enhanced_summary.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_report)

            return output_path
        except Exception as e:
            self.logger.error(f"Error generating enhanced summary report: {str(e)}")
            return None

