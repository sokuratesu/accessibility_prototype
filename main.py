#!/usr/bin/env python3
"""
Accessibility Prototype
A tool for testing website accessibility including Japanese-specific features.
"""

import os
import logging
import flet as ft

from src.config.config_manager import ConfigManager
from src.core.test_orchestrator import AccessibilityTestOrchestrator
from src.testers.axe_tester import AxeAccessibilityTester
from src.testers.wave_tester import WaveAccessibilityTester
from src.testers.japanese_tester import JapaneseAccessibilityTester
from src.testers.lighthouse_tester import LighthouseAccessibilityTester
from src.testers.pa11y_tester import Pa11yAccessibilityTester
from src.testers.htmlcs_tester import HTMLCSAccessibilityTester
from src.ui.app import AccessibilityTesterUI
from src.testers.w3c_tester import W3CTester
from src.testers.wcag22_tester import WCAG22Tester


def setup_logging():
    """Setup logging configuration."""
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "app.log")),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger("accessibility_prototype")


def initialize_testers(orchestrator, config_manager):
    """Initialize and register all testers with the orchestrator."""
    # Initialize Axe tester
    axe_tester = AxeAccessibilityTester(browser_type="chrome")
    orchestrator.register_tester("axe", axe_tester)

    # Initialize WAVE tester if API key is available
    wave_api_key = config_manager.get_api_key('wave')
    if wave_api_key:
        wave_tester = WaveAccessibilityTester(api_key=wave_api_key)
        orchestrator.register_tester("wave", wave_tester)

    # Initialize Japanese tester
    japanese_tester = JapaneseAccessibilityTester()
    orchestrator.register_tester("japanese_a11y", japanese_tester)

    # Initialize Lighthouse tester
    lighthouse_tester = LighthouseAccessibilityTester()
    orchestrator.register_tester("lighthouse", lighthouse_tester)

    # Initialize Pa11y tester
    pa11y_tester = Pa11yAccessibilityTester()
    orchestrator.register_tester("pa11y", pa11y_tester)

    # Initialize HTML CodeSniffer tester
    htmlcs_tester = HTMLCSAccessibilityTester()
    orchestrator.register_tester("htmlcs", htmlcs_tester)

    # Initialize W3C tester
    w3c_tester = W3CTester()
    orchestrator.register_tester("w3c_tools", w3c_tester)

    # Initialize WCAG 2.2 tester
    wcag22_tester = WCAG22Tester()
    orchestrator.register_tester("wcag22", wcag22_tester)

    return orchestrator


def init_app(page: ft.Page):
    """Initialize the application UI."""
    # Create orchestrator and initialize testers
    config_manager = ConfigManager()
    orchestrator = AccessibilityTestOrchestrator()
    orchestrator = initialize_testers(orchestrator, config_manager)

    # Set up the UI
    app = AccessibilityTesterUI(page)

    # We need to modify the UI class to support setting the orchestrator
    if hasattr(app, 'set_orchestrator'):
        app.set_orchestrator(orchestrator)


def main():
    """Main entry point for the application."""
    logger = setup_logging()
    logger.info("Starting Accessibility Prototype")

    # Start the UI
    ft.app(target=init_app)

    logger.info("Application closed")


if __name__ == "__main__":
    main()