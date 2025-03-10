"""
Configuration settings for the Twitch AI Bot.
Handles loading from environment variables and config files.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Global settings dictionary
_settings = {}


def load_settings(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load settings from .env file and optional JSON config file

    Args:
        config_file: Path to a JSON config file (optional)

    Returns:
        Dict containing all settings
    """
    global _settings

    # Load environment variables from .env file
    load_dotenv()

    # Initialize with environment variables
    settings = {
        # Bot settings
        "BOT_USERNAME": os.getenv("BOT_USERNAME", "TwitchAIBot"),
        "BOT_PREFIX": os.getenv("BOT_PREFIX", "!"),
        "BOT_CHANNELS": os.getenv("BOT_CHANNELS", "").split(","),

        # Twitch API
        "TWITCH_CLIENT_ID": os.getenv("TWITCH_CLIENT_ID", ""),
        "TWITCH_CLIENT_SECRET": os.getenv("TWITCH_CLIENT_SECRET", ""),
        "TWITCH_OAUTH_TOKEN": os.getenv("TWITCH_OAUTH_TOKEN", ""),
        "TWITCH_REFRESH_TOKEN": os.getenv("TWITCH_REFRESH_TOKEN", ""),

        # AI Service
        "AI_API_KEY": os.getenv("AI_API_KEY", ""),
        "AI_MODEL": os.getenv("AI_MODEL", "gpt-4-turbo"),
        "AI_TEMPERATURE": float(os.getenv("AI_TEMPERATURE", "0.7")),
        "AI_MAX_TOKENS": int(os.getenv("AI_MAX_TOKENS", "150")),

        # Context settings
        "CONTEXT_WINDOW_SIZE": int(os.getenv("CONTEXT_WINDOW_SIZE", "10")),
        "CONTEXT_MEMORY_LIMIT": int(os.getenv("CONTEXT_MEMORY_LIMIT", "20")),

        # Rate limiting
        "MESSAGE_RATE_LIMIT": float(os.getenv("MESSAGE_RATE_LIMIT", "1.5")),  # seconds between messages
        "API_RATE_LIMIT": float(os.getenv("API_RATE_LIMIT", "3.0")),  # seconds between API calls

        # Logging
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "LOG_TO_FILE": os.getenv("LOG_TO_FILE", "true").lower() == "true",
        "LOG_DIR": os.getenv("LOG_DIR", "logs"),

        # Performance
        "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "2")),
        "QUEUE_SIZE_LIMIT": int(os.getenv("QUEUE_SIZE_LIMIT", "100")),

        # Features
        "ENABLE_AUTO_RESPONSES": os.getenv("ENABLE_AUTO_RESPONSES", "true").lower() == "true",
        "RESPONSE_CHANCE": float(os.getenv("RESPONSE_CHANCE", "0.05")),  # 5% chance by default
        "ENABLE_COMMANDS": os.getenv("ENABLE_COMMANDS", "true").lower() == "true",
        "ENABLE_EMOTES": os.getenv("ENABLE_EMOTES", "true").lower() == "true",
        "ENABLE_EVENTS": os.getenv("ENABLE_EVENTS", "true").lower() == "true",
    }

    # Override with JSON config if provided
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    json_config = json.load(f)
                    # Deep merge the configurations
                    settings = _deep_merge(settings, json_config)
            except Exception as e:
                print(f"Error loading config file {config_file}: {e}")

    # Set up log level
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    settings["LOG_LEVEL_INT"] = log_level_map.get(settings["LOG_LEVEL"], logging.INFO)

    # Store settings globally
    _settings = settings

    return settings


def get_settings() -> Dict[str, Any]:
    """
    Get the current settings

    Returns:
        Dict containing all settings
    """
    global _settings

    # Load settings if not already loaded
    if not _settings:
        load_settings()

    return _settings


def update_settings(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update settings with new values

    Args:
        updates: Dictionary of settings to update

    Returns:
        Updated settings dictionary
    """
    global _settings

    # Make sure settings are loaded
    if not _settings:
        load_settings()

    # Update settings
    _settings = _deep_merge(_settings, updates)

    return _settings


def _deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries

    Args:
        dict1: Base dictionary
        dict2: Dictionary to merge (takes precedence)

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def save_settings(config_file: str) -> bool:
    """
    Save current settings to a JSON file

    Args:
        config_file: Path to save the config file

    Returns:
        Success status
    """
    global _settings

    try:
        # Make sure settings are loaded
        if not _settings:
            load_settings()

        # Create directory if it doesn't exist
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Save settings to file
        with open(config_path, 'w') as f:
            json.dump(_settings, f, indent=4)

        return True
    except Exception as e:
        print(f"Error saving settings to {config_file}: {e}")
        return False