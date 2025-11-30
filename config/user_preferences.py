"""
User Preferences Manager for Micro Durometer Application

This module provides simple JSON-based storage for user preferences.
Preferences are saved to user_preferences.json in the application directory.

Usage:
    from config.user_preferences import load_preferences, save_preference, get_preference

    # Load all preferences
    prefs = load_preferences()

    # Get a specific preference with default fallback
    calibration = get_preference('vickers_calibration', default=1.0)

    # Save a preference
    save_preference('vickers_calibration', 2.5)
"""

import json
import os
from typing import Any, Dict, Optional


PREFERENCES_FILE = "user_preferences.json"

# Default preferences
DEFAULT_PREFERENCES = {
    "vickers_calibration": 1.0,  # µm/pixel
    "vickers_load": 500.0,  # grams
    "viewport_maximized": False,  # viewport maximized state
    "viewport_width": None,  # last viewport width (None = use config default)
    "viewport_height": None,  # last viewport height (None = use config default)
    "last_project_folder": None,  # last opened project folder path
}


def load_preferences(prefs_path: str = PREFERENCES_FILE) -> Dict[str, Any]:
    """
    Load user preferences from JSON file.

    Args:
        prefs_path: Path to the preferences JSON file

    Returns:
        Dictionary containing all user preferences

    Example:
        >>> prefs = load_preferences()
        >>> print(prefs['vickers_calibration'])
        1.0
    """
    if not os.path.exists(prefs_path):
        print(f"[PREFERENCES] No preferences file found. Creating with defaults: {prefs_path}")
        save_preferences(DEFAULT_PREFERENCES, prefs_path)
        return DEFAULT_PREFERENCES.copy()

    try:
        with open(prefs_path, "r", encoding="utf-8") as f:
            prefs = json.load(f)

        # Merge with defaults (in case new preferences were added)
        merged_prefs = DEFAULT_PREFERENCES.copy()
        merged_prefs.update(prefs)

        return merged_prefs

    except (json.JSONDecodeError, IOError) as e:
        print(f"[PREFERENCES WARNING] Failed to load preferences: {e}. Using defaults.")
        return DEFAULT_PREFERENCES.copy()


def save_preferences(preferences: Dict[str, Any], prefs_path: str = PREFERENCES_FILE) -> bool:
    """
    Save all user preferences to JSON file.

    Args:
        preferences: Dictionary of all preferences to save
        prefs_path: Path to the preferences JSON file

    Returns:
        True if saved successfully, False otherwise

    Example:
        >>> prefs = {'vickers_calibration': 2.5, 'vickers_load': 1000}
        >>> save_preferences(prefs)
        True
    """
    try:
        with open(prefs_path, "w", encoding="utf-8") as f:
            json.dump(preferences, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"[PREFERENCES ERROR] Failed to save preferences: {e}")
        return False


def get_preference(key: str, default: Any = None, prefs_path: str = PREFERENCES_FILE) -> Any:
    """
    Get a single preference value.

    Args:
        key: Preference key to retrieve
        default: Default value if key doesn't exist
        prefs_path: Path to the preferences JSON file

    Returns:
        The preference value, or default if not found

    Example:
        >>> calibration = get_preference('vickers_calibration', default=1.0)
        >>> print(calibration)
        2.5
    """
    prefs = load_preferences(prefs_path)
    return prefs.get(key, default)


def save_preference(key: str, value: Any, prefs_path: str = PREFERENCES_FILE) -> bool:
    """
    Save a single preference value.

    Args:
        key: Preference key to save
        value: Value to save
        prefs_path: Path to the preferences JSON file

    Returns:
        True if saved successfully, False otherwise

    Example:
        >>> save_preference('vickers_calibration', 2.5)
        True
    """
    prefs = load_preferences(prefs_path)
    prefs[key] = value
    return save_preferences(prefs, prefs_path)


# Global preferences cache
_global_preferences = None


def get_preferences() -> Dict[str, Any]:
    """
    Get cached preferences. Loads from file if not already loaded.

    Returns:
        Dictionary containing all user preferences

    Example:
        >>> from config.user_preferences import get_preferences
        >>> prefs = get_preferences()
        >>> calibration = prefs['vickers_calibration']
    """
    global _global_preferences
    if _global_preferences is None:
        _global_preferences = load_preferences()
    return _global_preferences


def reload_preferences() -> Dict[str, Any]:
    """
    Force reload preferences from file, clearing cache.

    Returns:
        Dictionary containing all user preferences
    """
    global _global_preferences
    _global_preferences = load_preferences()
    return _global_preferences


if __name__ == "__main__":
    # Test the preferences system
    print("Testing user preferences system...")

    # Test saving
    print("\n=== Saving Preferences ===")
    save_preference("vickers_calibration", 2.5)
    save_preference("vickers_load", 1000)
    print("Saved: vickers_calibration = 2.5")
    print("Saved: vickers_load = 1000")

    # Test loading
    print("\n=== Loading Preferences ===")
    prefs = load_preferences()
    print(f"Loaded preferences: {prefs}")

    # Test getting single value
    print("\n=== Getting Single Preference ===")
    calibration = get_preference("vickers_calibration", default=1.0)
    load_value = get_preference("vickers_load", default=500.0)
    print(f"Calibration: {calibration} µm/pixel")
    print(f"Load: {load_value} g")

    # Test default fallback
    print("\n=== Testing Default Fallback ===")
    unknown = get_preference("unknown_key", default="default_value")
    print(f"Unknown key with default: {unknown}")

    print("\n=== Test Complete ===")
