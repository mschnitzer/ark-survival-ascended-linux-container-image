"""Configuration file parsing utilities."""

import configparser
from pathlib import Path
from typing import Optional


# Standard paths for ASA server configuration files
GAME_USER_SETTINGS_PATH = Path(
    "/home/gameserver/server-files/ShooterGame/Saved/Config/WindowsServer/GameUserSettings.ini"
)
GAME_INI_PATH = Path(
    "/home/gameserver/server-files/ShooterGame/Saved/Config/WindowsServer/Game.ini"
)


def parse_ini_file(path: Path) -> Optional[configparser.ConfigParser]:
    """
    Parse an INI configuration file.

    Args:
        path: Path to the INI file

    Returns:
        ConfigParser object if file exists, None otherwise
    """
    if not path.exists():
        return None

    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_game_user_settings() -> Optional[configparser.ConfigParser]:
    """Get parsed GameUserSettings.ini configuration."""
    return parse_ini_file(GAME_USER_SETTINGS_PATH)


def get_game_ini() -> Optional[configparser.ConfigParser]:
    """Get parsed Game.ini configuration."""
    return parse_ini_file(GAME_INI_PATH)


def parse_start_param(start_params: str, key: str) -> Optional[str]:
    """
    Extract a value from ASA start parameters string.

    Start parameters format: "?key1=value1?key2=value2 -key3=value3"

    Args:
        start_params: The start parameters string
        key: The parameter key to search for

    Returns:
        The parameter value if found, None otherwise

    Examples:
        >>> parse_start_param("?Port=7777?RCONPort=27020", "RCONPort")
        '27020'
        >>> parse_start_param("-WinLiveMaxPlayers=50", "WinLiveMaxPlayers")
        '50'
    """
    if not start_params:
        return None

    # Look for the key in the format "key="
    search_key = f"{key}="
    offset = start_params.find(search_key)

    if offset == -1:
        return None

    # Start after "key="
    offset += len(search_key)

    # Extract value until we hit a space or ? character
    value = []
    for char in start_params[offset:]:
        if char in (' ', '?'):
            break
        value.append(char)

    return ''.join(value) if value else None
