"""Domain errors that render through the standard API error envelope."""

from app.schemas import ApiErrorDetail


class AppValidationError(Exception):
    """Raised by services when caller input is unusable."""

    def __init__(self, message: str, details: list[ApiErrorDetail] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class ResourceNotFoundError(Exception):
    """Raised for a missing resource, and for one the caller does not own.

    Cross-user access is reported as "not found" so the API never confirms that
    another user's resource exists.
    """

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
        self.message = message
