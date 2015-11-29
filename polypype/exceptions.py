"""PolyPype-specific exceptions."""


class PolyPypeException(Exception):
    """Base exception class for all PolyPype exceptions."""
    pass


class PolyPypeOverflowException(PolyPypeException):
    """
    Raised when PolyPype is given a value that would overflow a c type.
    """
    pass


class PolyPypeTypeException(PolyPypeException):
    """
    Raised when PolyPype is given the wrong type for the time delta or
    parameters.
    """
    pass


class PolyPypeFileExistsException(PolyPypeException):
    """
    Raised when PolyPipe is told to open a file which already exists on disk.
    """
    pass


class PolyPypeArgumentException(PolyPypeException):
    """Raised when PolyPype is provided with invalid arguments."""
    pass
