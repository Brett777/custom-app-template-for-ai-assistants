"""
Configuration module for DataRobot Custom Application.

Environment variables can be set locally via .env or through
DataRobot Runtime Parameters (automatically prefixed with MLOPS_RUNTIME_PARAM_).
"""
import os
from functools import lru_cache


def get_env(key: str, default: str = "") -> str:
    """
    Get environment variable with DataRobot Runtime Parameter fallback.

    DataRobot prefixes runtime parameters with MLOPS_RUNTIME_PARAM_.
    This function checks the prefixed version first, then the standard name.

    Args:
        key: The base environment variable name (without prefix)
        default: Default value if not found

    Returns:
        The environment variable value or default
    """
    # Check DataRobot runtime parameter first
    dr_key = f"MLOPS_RUNTIME_PARAM_{key}"
    value = os.environ.get(dr_key)
    if value is not None:
        return value

    # Fall back to standard environment variable
    return os.environ.get(key, default)


def get_env_bool(key: str, default: bool = False) -> bool:
    """Get environment variable as boolean."""
    value = get_env(key, str(default).lower())
    return value.lower() in ("true", "1", "yes")


def get_env_int(key: str, default: int = 0) -> int:
    """Get environment variable as integer."""
    try:
        return int(get_env(key, str(default)))
    except ValueError:
        return default


@lru_cache
def get_settings():
    """Get application settings (cached)."""
    return Settings()


class Settings:
    """Application settings loaded from environment."""

    def __init__(self):
        # Server configuration
        self.port: int = get_env_int("PORT", 8080)
        self.debug: bool = get_env_bool("DEBUG", False)

        # Application-specific settings
        self.app_title: str = get_env("APP_TITLE", "Hello World")
