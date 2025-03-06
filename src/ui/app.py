"""
UI module for the Accessibility Tester application.
Provides a graphical user interface using Flet.
"""

import os
import flet as ft
import subprocess
import platform
from flet import Page, TextField, ElevatedButton, Text, ProgressBar, Column, SnackBar
import logging

from ..core.test_orchestrator import AccessibilityTestOrchestrator
from ..config.config_manager import ConfigManager
from ..utils.crawler import WebsiteCrawler


class AccessibilityTesterUI:
    """Main UI for the accessibility tester."""

    def __init__(self, page: Page):
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

        # Tools container
        self.tools_container = ft.Container(
            content=ft.Column([
                ft.Text("Select Testing Tools:", size=16, weight="bold"),
                self.axe_checkbox,
                self.wave_checkbox,
                self.wave_api_key_input,
                self.lighthouse_checkbox,
                self.pa11y_checkbox,
                self.htmlcs_checkbox,
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
                ft.Text("Japanese Accessibility Options:", size=16, weight="bold"),
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
                ft.Text("Crawling Options:", size=16, weight="bold"),
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
                ft.Text("Results:", size=16, weight="bold"),
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
        """Create a dialog for selecting pages to test."""

        """Initialize page selection dialog components."""
        self.url_checkboxes = []
        self.select_all_checkbox = None  # Will be created when needed

        self.url_list_view = ft.ListView(
            spacing=10,
            padding=20,
            auto_scroll=True,
            height=400
        )

        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            value=True,
            on_change=self.toggle_all_urls
        )

    def toggle_all_urls(self, e):
        """Toggle selection state for all URLs."""
        for checkbox in self.url_checkboxes:
            checkbox.value = self.select_all_checkbox.value
        self.page.update()

    def setup_ui(self):
        """Arrange UI components."""
        self.page.add(
            ft.Text("Accessibility Tester", size=24, weight="bold"),
            self.url_input,
            self.tools_container,
            self.japanese_checkbox,
            self.japanese_container,
            self.crawl_container,
            self.buttons_row,
            self.results_container
        )

    def set_orchestrator(self, orchestrator):
        """Set the test orchestrator.

        Args:
            orchestrator (AccessibilityTestOrchestrator): The test orchestrator
        """
        self.orchestrator = orchestrator

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

        # If not crawling, proceed with direct testing
        self._execute_tests(urls_to_test, selected_tools)

    def show_page_selection_dialog(self, urls, selected_tools):
        """Show dialog to select which pages to test.

        Args:
            urls (list): List of URLs found by crawler
            selected_tools (list): Selected testing tools
        """
        # Create a new container for the URL list
        url_list_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            height=400,
            width=600
        )

        # Reset checkbox list
        self.url_checkboxes = []

        # Add the "Select All" checkbox
        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            value=True,
            on_change=self.toggle_all_urls
        )
        url_list_column.controls.append(self.select_all_checkbox)

        # Add a checkbox for each URL
        for url in urls:
            # Create a checkbox for the URL
            url_checkbox = ft.Checkbox(
                label=url,
                value=True
            )
            self.url_checkboxes.append(url_checkbox)
            url_list_column.controls.append(url_checkbox)

        # Create buttons for the dialog
        def close_dialog(e):
            dialog.open = False

            # Re-enable test button
            self.test_button.disabled = False
            self.cancel_button.visible = False
            self.status_text.value = "Ready to test"
            self.progress_bar.visible = False

            self.page.update()

        def start_testing(e):
            dialog.open = False
            self.page.update()

            # Get selected URLs
            selected_urls = [
                checkbox.label
                for checkbox in self.url_checkboxes
                if checkbox.value
            ]

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

        # Create the dialog
        dialog = ft.AlertDialog(
            modal=True,  # Make it modal to ensure focus
            title=ft.Text("Select Pages to Test"),
            content=ft.Container(
                content=url_list_column,
                padding=10,
                width=600,
                height=450
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Test Selected", on_click=start_testing)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # Show the dialog
        self.page.dialog = dialog
        dialog.open = True
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
                results = self.orchestrator.run_tests(urls[0], selected_tools)

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

        # Create a settings dialog
        def close_dialog(e):
            settings_dialog.open = False
            self.page.update()

        def save_settings(e):
            # Save settings to config
            general_settings = self.config_manager.get_general_settings()
            general_settings["report_dir"] = report_dir_input.value
            general_settings["screenshot_on_violation"] = screenshot_checkbox.value
            general_settings["combined_report"] = combined_report_checkbox.value

            self.config_manager.save_config()
            self.show_snackbar("Settings saved")
            close_dialog(e)

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

        settings_dialog = ft.AlertDialog(
            title=ft.Text("Settings"),
            content=ft.Column([
                ft.Text("General Settings", size=16, weight="bold"),
                report_dir_input,
                screenshot_checkbox,
                combined_report_checkbox,
                ft.Container(height=20)  # Spacer
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Save", on_click=save_settings),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # Show the dialog
        self.page.dialog = settings_dialog
        settings_dialog.open = True
        self.page.update()