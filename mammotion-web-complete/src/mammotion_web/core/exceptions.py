"""Custom exceptions for the application."""


class MammotionWebError(Exception):
    """Base exception for Mammotion Web application."""
    
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthenticationError(MammotionWebError):
    """Raised when authentication fails."""
    pass


class DeviceError(MammotionWebError):
    """Raised when device operations fail."""
    pass


class ConfigurationError(MammotionWebError):
    """Raised when configuration is invalid."""
    pass


class WebSocketError(MammotionWebError):
    """Raised when WebSocket operations fail."""
    pass
