class DatabaseError(Exception):
    """Base class for database-related errors."""


class DuplicateUsernameError(DatabaseError):
    """Raised when trying to create a user with an existing username."""


class NotFoundError(DatabaseError):
    """Raised when an entity is not found."""
