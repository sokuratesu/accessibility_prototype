"""
Configuration manager for the application.
Manages API keys, settings, and other configuration data.
"""

import os
import json
import logging


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_file=None):
        """Initialize the config manager.

        Args:
            config_file (str, optional): Path to config file
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        if config_file is None:
            self.config_file = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        else:
            self.config_file = config_file

        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "api_keys": {},
                    "general": {
                        "report_dir": "reports",
                        "screenshot_on_violation": True,
                        "combined_report": True
                    },
                    "testers": {
                        "axe": {
                            "rules": "wcag21aa",
                            "browser": "chrome"
                        },
                        "wave": {
                            "reporttype": "2",
                            "timeout": 60
                        },
                        "lighthouse": {
                            "categories": ["accessibility"]
                        },
                        "pa11y": {
                            "standard": "WCAG2AA"
                        },
                        "htmlcs": {
                            "standard": "WCAG2AA"
                        },
                        "japanese_a11y": {
                            "form_zero": True,
                            "ruby_check": True,
                            "encoding": "utf-8"
                        }
                    }
                }

                # Save default config
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)

                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {
                "api_keys": {},
                "general": {},
                "testers": {}
            }

    def save_config(self):
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")

    def get_api_key(self, service):
        """Get API key for a service.

        Args:
            service (str): Service name

        Returns:
            str: API key or None
        """
        return self.config.get("api_keys", {}).get(service)

    def set_api_key(self, service, api_key):
        """Set API key for a service.

        Args:
            service (str): Service name
            api_key (str): API key
        """
        if "api_keys" not in self.config:
            self.config["api_keys"] = {}

        self.config["api_keys"][service] = api_key
        self.save_config()

    def get_general_settings(self):
        """Get general settings.

        Returns:
            dict: General settings
        """
        return self.config.get("general", {})

    def get_tester_settings(self, tester_id):
        """Get settings for a specific tester.

        Args:
            tester_id (str): Tester ID

        Returns:
            dict: Tester settings
        """
        return self.config.get("testers", {}).get(tester_id, {})

    def update_tester_settings(self, tester_id, settings):
        """Update settings for a specific tester.

        Args:
            tester_id (str): Tester ID
            settings (dict): Tester settings
        """
        if "testers" not in self.config:
            self.config["testers"] = {}

        if tester_id not in self.config["testers"]:
            self.config["testers"][tester_id] = {}

        self.config["testers"][tester_id].update(settings)
        self.save_config()

    def initialize_wave_api(self):
        """Initialize WAVE API from environment variables if not already set."""
        if not self.get_api_key("wave") and "WAVE_API_KEY" in os.environ:
            self.set_api_key("wave", os.environ["WAVE_API_KEY"])
            self.logger.info("Initialized WAVE API key from environment variable")