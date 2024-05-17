

class L402Exception(Exception):
    """Base class for all L402-related exceptions."""
    pass

class UnsupportedVersionError(L402Exception):
    """Raised when an unsupported L402 version is encountered."""
    pass

class InvalidL402HeaderError(L402Exception):
    """Raised when an invalid L402 header is encountered."""
    pass