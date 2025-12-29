class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class InvalidTokenError(DomainError):
    pass


class AuthenticationError(DomainError):
    pass


class AuthorizationError(DomainError):
    """Raised when user doesn't have permission to access resource"""
    pass
