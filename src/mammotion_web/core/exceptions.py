"""Custom application exceptions with proper error handling."""

from typing import Any, Dict, Optional


class MammotionWebError(Exception):
    """Base exception for all application errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}


class ConfigurationError(MammotionWebError):
    """Configuration related errors."""
    pass


class AuthenticationError(MammotionWebError):
    """Authentication related errors."""
    pass


class AuthorizationError(MammotionWebError):
    """Authorization related errors."""
    pass


class DeviceError(MammotionWebError):
    """Device communication errors."""
    pass


class DeviceNotFoundError(DeviceError):
    """Device not found error."""
    pass


class DeviceOfflineError(DeviceError):
    """Device offline error."""
    pass


class CommandError(DeviceError):
    """Device command execution error."""
    pass


class SessionError(MammotionWebError):
    """Session management errors."""
    pass


class ValidationError(MammotionWebError):
    """Input validation errors."""
    pass


class ExternalServiceError(MammotionWebError):
    """External service communication errors."""
    pass


class RateLimitError(MammotionWebError):
    """Rate limiting errors."""
    pass
