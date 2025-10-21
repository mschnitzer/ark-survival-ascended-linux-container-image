"""Custom exception classes for ASA Control."""


class AsaCtrlError(Exception):
    """Base exception for all ASA Control errors."""
    pass


class RconAuthenticationError(AsaCtrlError):
    """Raised when RCON authentication fails."""
    pass


class RconPasswordNotFoundError(AsaCtrlError):
    """Raised when RCON password cannot be found in configuration."""
    pass


class RconPortNotFoundError(AsaCtrlError):
    """Raised when RCON port cannot be found in configuration."""
    pass


class RconNotEnabledError(AsaCtrlError):
    """Raised when RCON is not enabled on the server."""
    pass


class ModAlreadyEnabledError(AsaCtrlError):
    """Raised when attempting to enable a mod that is already enabled."""
    pass
