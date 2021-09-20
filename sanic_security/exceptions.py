from sanic_security.utils import json


class SecurityError(Exception):
    """
    Sanic Security related error.

    Attributes:
        response (HTTPResponse): Security Error json response.

    Args:
        message (str): Human readable error message.
        code (int): HTTP error code.
    """

    def __init__(self, message: str, code: int):
        self.response = json(message, self.__class__.__name__, code)
        super().__init__(message, code)


class NotFoundError(SecurityError):
    def __init__(self, message):
        super().__init__(message, 404)


class DeletedError(SecurityError):
    def __init__(self, message):
        super().__init__(message, 404)


class AccountError(SecurityError):
    def __init__(self, message, code):
        super().__init__(message, code)


class DisabledError(AccountError):
    def __init__(self):
        super().__init__("This account has been disabled.", 401)


class UnverifiedError(AccountError):
    def __init__(self):
        super().__init__("Account requires verification.", 401)


class SessionError(SecurityError):
    def __init__(self, message, code=401):
        super().__init__(message, code)


class InvalidError(SessionError):
    def __init__(self):
        super().__init__("Session is invalid.", 401)


class ExpiredError(SessionError):
    def __init__(self):
        super().__init__("Session has expired", 401)


class InsufficientRolesError(SecurityError):
    def __init__(self):
        super().__init__("Insufficient roles required for this action.", 403)


class InsufficientPermissionsError(SecurityError):
    def __init__(self):
        super().__init__("Insufficient permissions required for this action.", 403)
