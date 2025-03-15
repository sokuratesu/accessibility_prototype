"""
Configuration manager for the application.
Manages API keys, settings, and other configuration data.
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
import base64

try:
    from cryptography.fernet import Fernet

    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    logging.warning("cryptography package not found. API key encryption disabled.")


@dataclass
class ToolConfig:
    """Configuration for an accessibility testing tool."""
    enabled: bool
    api_key: Optional[str] = None
    additional_settings: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_settings is None:
            self.additional_settings = {}


class SecureConfig:
    """Handles secure storage of sensitive configuration data."""

    def __init__(self, key_file=".config.key"):
        """Initialize the secure configuration handler.

        Args:
            key_file (str): Path to the encryption key file
        """
        self.key_file = key_file
        self.key = None
        self.cipher_suite = None

        if ENCRYPTION_AVAILABLE:
            self.key = self._load_or_create_key()
            self.cipher_suite = Fernet(self.key)

    def _load_or_create_key(self):
        """Load existing key or create a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()

        # Create new key
        key = Fernet.generate_key()

        # Save key with restricted permissions
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.key_file)), exist_ok=True)

            # Write key to file
            with open(self.key_file, 'wb') as f:
                f.write(key)

            # Set restrictive permissions on Unix-like systems
            if os.name == 'posix':
                os.chmod(self.key_file, 0o600)  # Only owner can read and write
        except Exception as e:
            logging.error(f"Error creating key file: {str(e)}")

        return key

    def encrypt_value(self, value: str) -> str:
        """Encrypt a string value.

        Args:
            value (str): Value to encrypt

        Returns:
            str: Base64-encoded encrypted value or original value if encryption is unavailable
        """
        if not value:
            return value

        if not ENCRYPTION_AVAILABLE or not self.cipher_suite:
            logging.warning("Encryption unavailable - storing value in plaintext")
            return value

        try:
            encrypted = self.cipher_suite.encrypt(value.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logging.error(f"Encryption error: {str(e)}")
            return value

    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt an encrypted value.

        Args:
            encrypted_value (str): Base64-encoded encrypted value

        Returns:
            str: Decrypted value or empty string if decryption fails
        """
        if not encrypted_value:
            return encrypted_value

        if not ENCRYPTION_AVAILABLE or not self.cipher_suite:
            logging.warning("Encryption unavailable - returning value as-is")
            return encrypted_value

        try:
            decoded = base64.b64decode(encrypted_value.encode())
            decrypted = self.cipher_suite.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logging.error(f"Decryption error: {str(e)}")
            return ""


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

        # Initialize secure config handler
        self.secure = SecureConfig()

        # Load configuration
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from file or create default."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Create default config
                default_config = {
                    "tools": {
                        "axe": {
                            "enabled": True,
                            "browser": "chrome",
                            "rules": "wcag21aa"
                        },
                        "wave": {
                            "enabled": False,
                            "api_key": self.secure.encrypt_value(""),
                            "additional_settings": {
                                "reporttype": "2",
                                "format": "json"
                            }
                        },
                        "lighthouse": {
                            "enabled": False,
                            "categories": ["accessibility"]
                        },
                        "pa11y": {
                            "enabled": False,
                            "standard": "WCAG2AA"
                        },
                        "htmlcs": {
                            "enabled": False,
                            "standard": "WCAG2AA",
                            "browser": "chrome"
                        },
                        "japanese_a11y": {
                            "enabled": False,
                            "form_zero": True,
                            "ruby_check": True,
                            "encoding": "utf-8"
                        },
                        "w3c_tools": {
                            "enabled": False,
                            "html_validator": True,
                            "css_validator": True,
                            "link_checker": True,
                            "nu_validator": False,
                            "aria_validator": True,
                            "dom_accessibility": True
                        },
                        "wcag22": {
                            "enabled": False
                        }
                    },
                    "general": {
                        "report_dir": "Reports",
                        "max_pages": 10,
                        "screenshot_on_violation": True,
                        "combined_report": True
                    },
                    "browser_settings": {
                        "screen_sizes": [
                            {"name": "Mobile", "width": 375, "height": 667, "enabled": True},
                            {"name": "Tablet", "width": 768, "height": 1024, "enabled": True},
                            {"name": "Desktop", "width": 1366, "height": 768, "enabled": True}
                        ],
                        "browsers": [
                            {"name": "Chrome", "enabled": True},
                            {"name": "Firefox", "enabled": False},
                            {"name": "Edge", "enabled": False},
                            {"name": "Safari", "enabled": False}
                        ]
                    }
                }

                # Save default config
                self.save_config(default_config)
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return {
                "tools": {},
                "general": {},
                "browser_settings": {
                    "screen_sizes": [],
                    "browsers": []
                }
            }

    def save_config(self, config: dict = None):
        """Save configuration to file.

        Args:
            config (dict, optional): Configuration to save
        """
        if config is not None:
            self.config = config

        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving config: {str(e)}")

    def get_tool_config(self, tool_name: str) -> ToolConfig:
        """Get configuration for specific tool.

        Args:
            tool_name (str): Tool name

        Returns:
            ToolConfig: Tool configuration
        """
        tool_config = self.config.get('tools', {}).get(tool_name, {})

        # Handle API key specially to decrypt it
        api_key = None
        if 'api_key' in tool_config:
            api_key = self.secure.decrypt_value(tool_config.get('api_key', ''))

        return ToolConfig(
            enabled=tool_config.get('enabled', False),
            api_key=api_key,
            additional_settings={k: v for k, v in tool_config.items()
                                 if k not in ('enabled', 'api_key')}
        )

    def set_api_key(self, tool_name: str, api_key: str):
        """Set API key for a specific tool.

        Args:
            tool_name (str): Tool name
            api_key (str): API key
        """
        if 'tools' not in self.config:
            self.config['tools'] = {}

        if tool_name not in self.config['tools']:
            self.config['tools'][tool_name] = {}

        # Encrypt the API key
        encrypted_key = self.secure.encrypt_value(api_key)

        # Update the configuration
        self.config['tools'][tool_name].update({
            'enabled': True,
            'api_key': encrypted_key
        })

        # Save the configuration
        self.save_config()

        # Debug output
        self.logger.debug(f"Saved {tool_name} API key (encrypted)")

    def get_api_key(self, tool_name: str) -> str:
        """Get decrypted API key for a tool.

        Args:
            tool_name (str): Tool name

        Returns:
            str: Decrypted API key or empty string
        """
        encrypted_key = self.config.get('tools', {}).get(tool_name, {}).get('api_key', '')
        return self.secure.decrypt_value(encrypted_key)

    def get_general_settings(self) -> dict:
        """Get general settings.

        Returns:
            dict: General settings
        """
        return self.config.get('general', {})

    def get_browser_settings(self) -> dict:
        """Get browser and screen size settings.

        Returns:
            dict: Browser settings
        """
        return self.config.get('browser_settings', {
            'screen_sizes': [
                {"name": "Mobile", "width": 375, "height": 667, "enabled": True},
                {"name": "Tablet", "width": 768, "height": 1024, "enabled": True},
                {"name": "Desktop", "width": 1366, "height": 768, "enabled": True}
            ],
            'browsers': [
                {"name": "Chrome", "enabled": True},
                {"name": "Firefox", "enabled": False},
                {"name": "Edge", "enabled": False},
                {"name": "Safari", "enabled": False}
            ]
        })

    def update_browser_settings(self, settings: dict):
        """Update browser and screen size settings.

        Args:
            settings (dict): New browser settings
        """
        if 'browser_settings' not in self.config:
            self.config['browser_settings'] = {}

        self.config['browser_settings'].update(settings)
        self.save_config()

    def get_enabled_screen_sizes(self) -> list:
        """Get list of enabled screen sizes.

        Returns:
            list: Enabled screen sizes
        """
        screen_sizes = self.config.get('browser_settings', {}).get('screen_sizes', [])
        return [size for size in screen_sizes if size.get('enabled', False)]

    def get_enabled_browsers(self) -> list:
        """Get list of enabled browsers.

        Returns:
            list: Enabled browsers
        """
        browsers = self.config.get('browser_settings', {}).get('browsers', [])
        return [browser for browser in browsers if browser.get('enabled', False)]

    def get_w3c_enabled_tests(self) -> list:
        """Get list of enabled W3C tests.

        Returns:
            list: Enabled W3C tests
        """
        w3c_config = self.config.get('tools', {}).get('w3c_tools', {})
        enabled_tests = []

        # Check each test type
        for test in ['html_validator', 'css_validator', 'link_checker',
                     'nu_validator', 'aria_validator', 'dom_accessibility']:
            if w3c_config.get(test, False):
                enabled_tests.append(test)

        return enabled_tests

    def update_w3c_settings(self, settings: dict):
        """Update W3C tool settings.

        Args:
            settings (dict): New W3C settings
        """
        if 'tools' not in self.config:
            self.config['tools'] = {}

        if 'w3c_tools' not in self.config['tools']:
            self.config['tools']['w3c_tools'] = {'enabled': False}

        self.config['tools']['w3c_tools'].update(settings)
        self.save_config()

    def initialize_wave_api(self, api_key: str = None):
        """Initialize or update WAVE API configuration.

        Args:
            api_key (str, optional): API key to use. If None, try to use environment variable.

        Returns:
            str: Decrypted API key or empty string
        """
        # Check environment variable if no key provided
        if api_key is None:
            import os
            api_key = os.environ.get("WAVE_API_KEY", "")

        if api_key:
            self.set_api_key("wave", api_key)
            return api_key

        # Return existing key if any
        return self.get_api_key("wave")

    def update_tool_settings(self, tool_name: str, settings: dict):
        """Update settings for a specific tool.

        Args:
            tool_name (str): Tool name
            settings (dict): Tool settings
        """
        if 'tools' not in self.config:
            self.config['tools'] = {}

        if tool_name not in self.config['tools']:
            self.config['tools'][tool_name] = {}

        # Handle API key specially
        if 'api_key' in settings and settings['api_key']:
            settings['api_key'] = self.secure.encrypt_value(settings['api_key'])

        self.config['tools'][tool_name].update(settings)
        self.save_config()

    def update_general_settings(self, settings: dict):
        """Update general settings.

        Args:
            settings (dict): General settings
        """
        if 'general' not in self.config:
            self.config['general'] = {}

        self.config['general'].update(settings)
        self.save_config()