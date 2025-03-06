"""
Japanese Accessibility Configuration
This module contains configuration data for Japanese-specific accessibility testing.
"""

JAPANESE_CONFIG = {
    'encoding': ['utf-8', 'shift_jis', 'euc-jp'],
    'typography': {
        "min_font_size": 12,  # Minimum font size for Japanese text
        "line_height": 1.5,   # Minimum line height ratio
        "font_families": [
            "Meiryo",
            "Hiragino Kaku Gothic Pro",
            "MS PGothic",
            "Yu Gothic",
            "游ゴシック",
            "メイリオ",
            "ヒラギノ角ゴ Pro"
        ]
    },
    'input_methods': ['ime-mode: active'],
    'standards': {
        'jis': 'JIS X 8341-3:2016',
        'wcag': 'WCAG 2.1'
    },
    "ime": {
        "required": True
    },
    "ruby": {
        "required_for_joyokanji_level": 2  # Level in joyo kanji that requires ruby
    },
    "form_zero": {
        "session_timeout_warning": True,
        "auto_save": True,
        "reenter_data": True
    }
}

# Mapping of Japanese accessibility issues to WCAG/JIS standards
# Japanese accessibility testing configuration
JAPANESE_CONFIG = {
    "typography": {
        "min_font_size": 12,  # Minimum font size for Japanese text
        "line_height": 1.5,   # Minimum line height ratio
        "font_families": [
            "Meiryo",
            "Hiragino Kaku Gothic Pro",
            "MS PGothic",
            "Yu Gothic",
            "游ゴシック",
            "メイリオ",
            "ヒラギノ角ゴ Pro"
        ]
    },
    "encoding": ["utf-8", "shift_jis", "euc-jp"],
    "ime": {
        "required": True
    },
    "ruby": {
        "required_for_joyokanji_level": 2  # Level in joyo kanji that requires ruby
    },
    "form_zero": {
        "session_timeout_warning": True,
        "auto_save": True,
        "reenter_data": True
    }
}

# Mapping of Japanese checks to WCAG and JIS criteria
JAPANESE_WCAG_MAPPING = {
    "encoding": {
        "wcag": "3.1.1",
        "level": "A",
        "jis": "JIS X 8341-3:2016 7.3.1",
        "category": "Language"
    },
    "typography": {
        "wcag": "1.4.8",
        "level": "AAA",
        "jis": "JIS X 8341-3:2016 7.1.4.8",
        "category": "Presentation"
    },
    "font_size": {
        "wcag": "1.4.4",
        "level": "AA",
        "jis": "JIS X 8341-3:2016 7.1.4.4",
        "category": "Presentation"
    },
    "line_height": {
        "wcag": "1.4.8",
        "level": "AAA",
        "jis": "JIS X 8341-3:2016 7.1.4.8",
        "category": "Presentation"
    },
    "font_families": {
        "wcag": "1.4.8",
        "level": "AAA",
        "jis": "JIS X 8341-3:2016 7.1.4.8",
        "category": "Presentation"
    },
    "input_methods": {
        "wcag": "3.2.2",
        "level": "A",
        "jis": "JIS X 8341-3:2016 7.3.2.2",
        "category": "Input"
    },
    "ruby_text": {
        "wcag": "3.1.5",
        "level": "AAA",
        "jis": "JIS X 8341-3:2016 7.3.1.5",
        "category": "Language"
    },
    "screen_reader": {
        "wcag": "1.3.1",
        "level": "A",
        "jis": "JIS X 8341-3:2016 7.1.3.1",
        "category": "Structure"
    },
    "text_resize": {
        "wcag": "1.4.4",
        "level": "AA",
        "jis": "JIS X 8341-3:2016 7.1.4.4",
        "category": "Presentation"
    },
    "color_contrast": {
        "wcag": "1.4.3",
        "level": "AA",
        "jis": "JIS X 8341-3:2016 7.1.4.3",
        "category": "Presentation"
    },
    "form_zero": {
        "wcag": "3.3.4",
        "level": "AA",
        "jis": "JIS X 8341-3:2016 7.3.3.4",
        "category": "Input"
    },
    "keyboard_navigation": {
        "wcag": "2.1.1",
        "level": "A",
        "jis": "JIS X 8341-3:2016 7.2.1.1",
        "category": "Operation"
    },
    "focus_visibility": {
        "wcag": "2.4.7",
        "level": "AA",
        "jis": "JIS X 8341-3:2016 7.2.4.7",
        "category": "Operation"
    },
    "error_identification": {
        "wcag": "3.3.1",
        "level": "A",
        "jis": "JIS X 8341-3:2016 7.3.3.1",
        "category": "Input"
    },
    "timeout_handling": {
        "wcag": "2.2.1",
        "level": "A",
        "jis": "JIS X 8341-3:2016 7.2.2.1",
        "category": "Time"
    }
}