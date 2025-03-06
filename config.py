import os
from dataclasses import dataclass
from typing import Dict, Optional
import json
from cryptography.fernet import Fernet
import base64


@dataclass
class ToolConfig:
    enabled: bool
    api_key: Optional[str] = None
    additional_settings: Dict = None

    def __post_init__(self):
        if self.additional_settings is None:
            self.additional_settings = {}

class AccessibilityConfig:
    def __init__(self):
        self.config_file = "accessibility_config.json"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._create_default_config()

    def _create_default_config(self):
        default_config = {
            "tools": {
                "axe": {
                    "enabled": True,
                    "browser": "chrome"
                },
                "wave": {
                    "enabled": False,
                    "api_key": self.secure.encrypt_value("AUV3YPQa5013")  # Encrypt the default key
                },
                "lighthouse": {
                    "enabled": False
                },
                "pa11y": {
                    "enabled": False
                },
                "htmlcs": {
                    "enabled": False,
                    "browser": "chrome"
                }
            },
            "general": {
                "report_dir": "Reports",
                "max_pages": 10,
                "screenshot_on_violation": True,
                "combined_report": True
            }
        }
        self.save_config(default_config)
        return default_config

    def save_config(self, config: dict = None):
        """Save configuration to file"""
        if config is not None:
            self.config = config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_tool_config(self, tool_name: str) -> ToolConfig:
        """Get configuration for specific tool"""
        tool_config = self.config['tools'].get(tool_name, {})
        return ToolConfig(
            enabled=tool_config.get('enabled', False),
            api_key=tool_config.get('api_key'),
            additional_settings=tool_config.get('additional_settings', {})
        )

    def set_api_key(self, tool_name: str, api_key: str):
        """Set API key for a specific tool"""
        if tool_name not in self.config['tools']:
            self.config['tools'][tool_name] = {}
        self.config['tools'][tool_name]['api_key'] = api_key
        self.save_config()

    def get_general_settings(self) -> dict:
        """Get general settings"""
        return self.config.get('general', {})


class SecureConfig:
    def __init__(self):
        self.key_file = ".config.key"
        self.key = self._load_or_create_key()
        self.cipher_suite = Fernet(self.key)

    def _load_or_create_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as f:
            f.write(key)
        return key

    def encrypt_value(self, value: str) -> str:
        if not value:
            return value
        encrypted = self.cipher_suite.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        if not encrypted_value:
            return encrypted_value
        try:
            decoded = base64.b64decode(encrypted_value.encode())
            decrypted = self.cipher_suite.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return ""


class ConfigManager:
    def __init__(self):
        self.config_file = "accessibility_config.json"
        self.secure = SecureConfig()
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._create_default_config()

    def _create_default_config(self):
        default_config = {
            "tools": {
                "axe": {
                    "enabled": True,
                    "browser": "chrome"
                },
                "wave": {
                    "enabled": False,
                    "api_key": self.secure.encrypt_value("AUV3YPQa5013")  # Encrypt the default key
                },
                "lighthouse": {
                    "enabled": False
                },
                "pa11y": {
                    "enabled": False
                },
                "htmlcs": {
                    "enabled": False,
                    "browser": "chrome"
                }
            },
            "general": {
                "report_dir": "Reports",
                "max_pages": 10,
                "screenshot_on_violation": True,
                "combined_report": True
            }
        }
        self.save_config(default_config)
        return default_config

    def setup_wave_api(self, api_key: str):
        """Setup WAVE API configuration"""
        if 'wave' not in self.config['tools']:
            self.config['tools']['wave'] = {}

        # Encrypt and store the API key
        self.config['tools']['wave'].update({
            'enabled': True,
            'api_key': self.secure.encrypt_value(api_key),
            'additional_settings': {
                'report_type': '2',  # detailed report
                'format': 'json'
            }
        })

        self.save_config()

    def initialize_wave_api(self, api_key: str = "AUV3YPQa5013"):
        """Initialize or update WAVE API configuration"""
        if 'wave' not in self.config['tools']:
            self.config['tools']['wave'] = {}

        # Encrypt the API key
        encrypted_key = self.secure.encrypt_value(api_key)

        self.config['tools']['wave'].update({
            'enabled': True,
            'api_key': encrypted_key
        })

        self.save_config()
        return self.secure.decrypt_value(encrypted_key)

    def debug_wave_api(self):
        """Debug WAVE API configuration"""
        wave_config = self.config['tools'].get('wave', {})
        encrypted_key = wave_config.get('api_key', '')
        decrypted_key = self.secure.decrypt_value(encrypted_key)
        print("\nWAVE API Debug Information:")
        print(f"WAVE configuration: {wave_config}")
        print(f"Encrypted key: {encrypted_key}")
        print(f"Decrypted key: {decrypted_key}")
        print(f"Key valid: {bool(decrypted_key)}\n")

    def save_config(self, config=None):
        if config:
            self.config = config
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_api_key(self, tool_name: str) -> str:
        """Get decrypted API key"""
        encrypted_key = self.config['tools'].get(tool_name, {}).get('api_key', '')
        return self.secure.decrypt_value(encrypted_key)

    def set_api_key(self, tool_name: str, api_key: str):
        """Set encrypted API key"""
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
        print(f"Saved {tool_name} API key:")
        print(f"Original: {api_key}")
        print(f"Encrypted: {encrypted_key}")
        print(f"Decrypted: {self.secure.decrypt_value(encrypted_key)}")