"""
Simple Configuration Manager for Micro Durometer Application

This module provides a simple function to load configuration from config.ini
using Python's configparser. It includes hardcoded defaults and console warnings
for missing or corrupted values.

Usage:
    from config.simple_config import load_config

    config = load_config()
    width = config['Window']['width']
    title = config['Window']['title']
"""

import configparser
import os
import sys
from pathlib import Path


# Hardcoded defaults
DEFAULTS = {
    "Window": {"title": "Micro Durometer", "width": 1280, "height": 768, "min_width": 1280, "min_height": 768},
    "Paths": {"dpg_ini_file": "dpg.ini", "icon_small": "icons/Icon.ico", "icon_large": "icons/Icon.ico"},
    "Fonts": {
        "default_font_path": "fonts/Inter-Regular.otf",
        "default_font_size": 20,
        "italic_font_path": "fonts/Roboto/static/Roboto-LightItalic.ttf",
        "italic_font_size": 20,
        "bold_font_path": "fonts/Roboto/static/Roboto-Bold.ttf",
        "bold_font_size": 20,
        "h1_font_path": "fonts/Roboto/static/Roboto-Bold.ttf",
        "h1_font_size": 30,
    },
    "Theme.Padding": {
        "window_padding_x": 8,
        "window_padding_y": 8,
        "frame_padding_x": 20,
        "frame_padding_y": 4,
        "cell_padding_x": 4,
        "cell_padding_y": 2,
    },
    "Theme.Spacing": {"item_spacing_x": 8, "item_spacing_y": 4, "item_inner_spacing_x": 4, "item_inner_spacing_y": 4, "indent_spacing": 20},
    "Theme.Sizes": {"scrollbar_size": 14, "grab_min_size": 20},
    "Theme.Borders": {"window_border_size": 1, "popup_border_size": 1, "frame_border_size": 0},
    "Theme.Rounding": {
        "window_rounding": 12,
        "child_rounding": 12,
        "frame_rounding": 4,
        "popup_rounding": 12,
        "scrollbar_rounding": 9,
        "grab_rounding": 12,
        "tab_rounding": 12,
    },
    "UI.ProcessingTab": {"controls_width": 400},
    "UI.FileDialog": {"min_width": 400, "min_height": 300},
    "UI.FileDialog.Colors": {
        "default_file": "#96FF96FF",
        "jpg_file": "#FF0000FF",
        "png_file": "#FFFF00FF",
        "jpeg_file": "#FF0000FF",
        "bmp_file": "#00FFFFFF",
    },
    "UI.Labels": {
        "select_image_prompt": "Select a Image to Use",
        "import_button": "Import Image",
        "plot_title": "Processing",
        "x_axis_label": "Width",
        "y_axis_label": "Height",
        "processing_tab": "Processing",
    },
}


def _get_value(parser, section, key, default_value=None):
    """
    Safely get a value from config parser with type conversion.

    Priority:
    1. If value exists in config.ini and is valid, use it
    2. If value doesn't exist in config.ini but exists in DEFAULTS, use default
    3. If value doesn't exist in either place, terminate program with error

    Args:
        parser: ConfigParser instance
        section: Section name
        key: Key name
        default_value: Default value from DEFAULTS (None if key not in DEFAULTS)

    Returns:
        The configuration value with appropriate type conversion
    """
    # Check if value exists in config.ini
    if parser.has_section(section) and parser.has_option(section, key):
        try:
            value = parser.get(section, key)

            # Type conversion based on default value type (if available)
            if default_value is not None:
                if isinstance(default_value, int):
                    return int(value)
                elif isinstance(default_value, float):
                    return float(value)
                elif isinstance(default_value, bool):
                    return parser.getboolean(section, key)

            # Return as string if no type hint from default
            return value

        except (ValueError, configparser.Error) as e:
            # Value exists but is corrupted
            if default_value is not None:
                print(f"[CONFIG WARNING] Error reading [{section}] {key}: {e}. Using default: {default_value}")
                return default_value
            else:
                print(f"[CONFIG ERROR] Error reading [{section}] {key}: {e}")
                print(f"[CONFIG ERROR] No default value defined for [{section}] {key}")
                print(f"[CONFIG ERROR] Cannot continue. Please fix config.ini or add default value.")
                sys.exit(1)

    # Value not in config.ini
    if default_value is not None:
        print(f"[CONFIG WARNING] Key '{key}' not found in section [{section}]. Using default: {default_value}")
        return default_value
    else:
        # No value in config.ini and no default
        print(f"[CONFIG ERROR] Key '{key}' not found in section [{section}]")
        print(f"[CONFIG ERROR] No default value defined for [{section}] {key}")
        print(f"[CONFIG ERROR] Cannot continue. Please add this key to config.ini or define a default value.")
        sys.exit(1)


def load_config(config_path="config.ini"):
    """
    Load configuration from config.ini file.

    Args:
        config_path (str): Path to the config.ini file. Defaults to 'config.ini'
                          in the current working directory.

    Returns:
        dict: Nested dictionary containing all configuration values.
              Access values like: config['Window']['width']

    Example:
        >>> config = load_config()
        >>> print(config['Window']['title'])
        'Micro Durometer'
    """
    config = {}
    parser = configparser.ConfigParser()

    # Check if config file exists
    if not os.path.exists(config_path):
        print(f"[CONFIG WARNING] config.ini not found at '{config_path}'. Using all default values.")
        return DEFAULTS.copy()

    try:
        parser.read(config_path, encoding="utf-8")
    except Exception as e:
        print(f"[CONFIG ERROR] Failed to read config.ini: {e}. Using all default values.")
        return DEFAULTS.copy()

    # Step 1: Load all sections and keys from config.ini
    for section in parser.sections():
        if section not in config:
            config[section] = {}
        for key in parser.options(section):
            # Get default value if it exists in DEFAULTS
            default_value = DEFAULTS.get(section, {}).get(key, None)
            config[section][key] = _get_value(parser, section, key, default_value)

    # Step 2: Add any missing keys from DEFAULTS (with warnings)
    for section, keys in DEFAULTS.items():
        if section not in config:
            config[section] = {}
        for key, default_value in keys.items():
            if key not in config[section]:
                config[section][key] = _get_value(parser, section, key, default_value)

    return config


def hex_to_rgba(hex_color):
    """
    Convert hex color string to RGBA tuple.

    Args:
        hex_color (str): Hex color in format '#RRGGBBAA'

    Returns:
        tuple: (R, G, B, A) values in range 0-255

    Example:
        >>> hex_to_rgba('#96FF96FF')
        (150, 255, 150, 255)
    """
    try:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 8:
            raise ValueError("Hex color must be 8 characters (RRGGBBAA)")

        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(hex_color[6:8], 16)

        return (r, g, b, a)
    except (ValueError, IndexError) as e:
        print(f"[CONFIG WARNING] Invalid hex color '{hex_color}': {e}. Using default.")
        return (255, 255, 255, 255)  # White default


def get_path(config, section, key):
    """
    Get a path from config and convert it to a Path object.
    Automatically normalizes path separators for the current OS.

    Args:
        config (dict): Configuration dictionary
        section (str): Section name
        key (str): Key name

    Returns:
        Path: Path object with normalized separators

    Example:
        >>> config = load_config()
        >>> icon_path = get_path(config, 'Paths', 'icon_small')
    """
    path_str = config[section][key]
    return Path(path_str)


# For convenience, create a global config instance
_global_config = None


def get_config():
    """
    Get the global configuration instance. Loads it if not already loaded.

    Returns:
        dict: Global configuration dictionary

    Example:
        >>> from config.simple_config import get_config
        >>> config = get_config()
        >>> width = config['Window']['width']
    """
    global _global_config
    if _global_config is None:
        _global_config = load_config()
    return _global_config


if __name__ == "__main__":
    # Test the configuration loader
    print("Testing configuration loader...")
    config = load_config()

    print("\n=== Window Configuration ===")
    print(f"Title: {config['Window']['title']}")
    print(f"Size: {config['Window']['width']}x{config['Window']['height']}")

    print("\n=== Font Configuration ===")
    print(f"Default Font: {config['Fonts']['default_font_path']} ({config['Fonts']['default_font_size']}pt)")

    print("\n=== Theme Configuration ===")
    print(f"Window Padding: ({config['Theme.Padding']['window_padding_x']}, {config['Theme.Padding']['window_padding_y']})")
    print(f"Window Rounding: {config['Theme.Rounding']['window_rounding']}")

    print("\n=== UI Colors ===")
    print(
        f"Default File Color: {config['UI.FileDialog.Colors']['default_file']} -> {hex_to_rgba(config['UI.FileDialog.Colors']['default_file'])}"
    )

    print("\n=== Paths ===")
    icon_path = get_path(config, "Paths", "icon_small")
    print(f"Icon Path: {icon_path} (exists: {icon_path.exists()})")
